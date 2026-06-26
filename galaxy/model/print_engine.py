import os
from datetime import UTC, datetime

from jinja2 import Template
from sqlalchemy import text

from galaxy.config import load_site_config
from galaxy.database.connection import get_engine
from galaxy.model.document import get_document
from galaxy.model.repository import get_doctype_fields, get_runtime_meta


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


def _get_print_format(doctype: str, format_name: str = "Standard") -> dict | None:
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT name, doctype, template_html, template_css, font_family
                FROM "tabPrintFormat"
                WHERE (doctype = :doctype OR doctype = '*') AND name = :name AND enabled = TRUE
                ORDER BY idx LIMIT 1
            """),
            {"doctype": doctype, "name": format_name},
        ).mappings().one_or_none()
    return dict(row) if row else None


def _get_letterhead(name: str = "Default") -> dict | None:
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT name, letterhead_html
                FROM "tabLetterhead"
                WHERE name = :name AND enabled = TRUE
            """),
            {"name": name},
        ).mappings().one_or_none()
    return dict(row) if row else None


def _render_html(doctype: str, docname: str, format_name: str = "Standard", letterhead: str | None = None) -> str:
    doc = get_document(doctype, docname)
    if doc is None:
        raise ValueError(f"Document '{docname}' not found in '{doctype}'.")
    fields = get_doctype_fields(doctype)
    pf = _get_print_format(doctype, format_name)
    if pf is None:
        pf = _get_print_format("*", "Standard")
    if pf is None:
        raise ValueError(f"No print format '{format_name}' found for '{doctype}'.")
    template_html = pf.get("template_html", "")
    template_css = pf.get("template_css", "")
    font_family = pf.get("font_family", "'Segoe UI', Tahoma, sans-serif")
    lh_html = ""
    if letterhead:
        lh = _get_letterhead(letterhead)
        if lh:
            lh_html = lh.get("letterhead_html", "")
    ctx = {
        "doc": doc,
        "doctype": doctype,
        "docname": docname,
        "fields": fields,
        "format": pf,
        "letterhead_html": lh_html,
        "now": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "company_name": "",
        "address": "",
    }
    if font_family:
        font_css = f"body {{ font-family: {font_family}; }}"
        if template_css:
            template_css = font_css + "\n" + template_css
        else:
            template_css = font_css
    full_html = "<!DOCTYPE html>\n<html dir=\"auto\">\n<head>\n<meta charset=\"utf-8\">\n"
    if template_css:
        full_html += f"<style>\n{template_css}\n</style>\n"
    full_html += "</head>\n<body>\n"
    if lh_html:
        t = Template(lh_html)
        full_html += t.render(**ctx) + "\n"
    t = Template(template_html)
    full_html += t.render(**ctx) + "\n"
    full_html += "</body>\n</html>"
    return full_html


def render_print_html(doctype: str, docname: str, format_name: str = "Standard", letterhead: str | None = None) -> str:
    return _render_html(doctype, docname, format_name, letterhead)


def render_print_pdf(doctype: str, docname: str, format_name: str = "Standard", letterhead: str | None = None) -> bytes:
    html = _render_html(doctype, docname, format_name, letterhead)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("playwright is required for PDF rendering. Install with: pip install playwright && python -m playwright install chromium")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"})
        browser.close()
    return pdf_bytes


__all__ = ["render_print_html", "render_print_pdf"]
