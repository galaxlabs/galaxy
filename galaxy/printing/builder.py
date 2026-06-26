from datetime import UTC, datetime

from jinja2 import Template


def get_field_variables(fields: list[dict], doc: dict) -> dict:
    """Returns a flat dict of fieldname → value and type info for template use."""
    vars = {}
    for f in fields:
        fn = f["fieldname"]
        ft = f["fieldtype"]
        val = doc.get(fn)
        vars[f"field_{fn}"] = val
        vars[f"{fn}_type"] = ft
        vars[f"{fn}_label"] = f.get("label", fn)
        if ft in ("Check",):
            vars[f"{fn}_checked"] = "checked" if val else ""
            vars[f"{fn}_yesno"] = "Yes" if val else "No"
        if ft in ("Date", "Datetime"):
            vars[f"{fn}_formatted"] = str(val) if val else ""
    return vars


def build_template_from_fields(doctype: str, fields: list[dict], selected: list[str] | None = None, conditional: dict[str, str] | None = None) -> str:
    """Build a print template HTML from selected fields with optional conditionals."""
    if selected is None:
        selected = [f["fieldname"] for f in fields]
    field_map = {f["fieldname"]: f for f in fields}
    parts = []
    parts.append("""<div style="max-width:800px;margin:0 auto;padding:20px;">""")
    parts.append("""<h1 style="text-align:center;color:#2563eb;">{{ doctype }}</h1>""")
    parts.append("""<p style="text-align:center;color:#666;">{{ doc.name }}</p>""")
    parts.append("""<hr style="border:none;border-top:2px solid #2563eb;">""")
    parts.append("""<table style="width:100%;border-collapse:collapse;">""")
    for fn in selected:
        f = field_map.get(fn)
        if f is None:
            continue
        label = f.get("label", fn)
        ft = f["fieldtype"]
        cond = (conditional or {}).get(fn, "")
        row = _field_row(fn, label, ft, cond)
        parts.append(row)
    parts.append("</table>")
    parts.append("""<hr style="margin-top:32px;border:none;border-top:1px solid #e5e7eb;">""")
    parts.append("""<p style="text-align:center;font-size:12px;color:#9ca3af;">Generated {{ now }}</p>""")
    parts.append("</div>")
    return "\n".join(parts)


def _field_row(fn: str, label: str, ftype: str, condition: str) -> str:
    if condition:
        condition_jinja = condition.replace("{{", "{{ ").replace("}}", " }}")
        row = "{% if " + condition_jinja + " %}\n"
    else:
        row = ""
    if ftype in ("Check",):
        row += f"""<tr><td style="padding:8px 12px;font-weight:600;width:200px;">{label}</td><td style="padding:8px 12px;">{{% if doc.{fn} %}}Yes{{% else %}}No{{% endif %}}</td></tr>"""
    elif ftype in ("Text", "Small Text", "Long Text", "Code"):
        row += f"""<tr><td style="padding:8px 12px;font-weight:600;width:200px;vertical-align:top;">{label}</td><td style="padding:8px 12px;white-space:pre-wrap;">{{{{ doc.{fn} }}}}</td></tr>"""
    else:
        row += f"""<tr><td style="padding:8px 12px;font-weight:600;width:200px;">{label}</td><td style="padding:8px 12px;">{{{{ doc.{fn} }}}}</td></tr>"""
    if condition:
        row += "{% endif %}\n"
    return row


def render_conditional_html(doctype: str, docname: str, fields: list[dict], template_html: str) -> str:
    """Render a template built by build_template_from_fields against a document."""
    doc = {f["fieldname"]: docname for f in fields}
    ctx = {
        "doc": doc,
        "doctype": doctype,
        "docname": docname,
        "now": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
    }
    t = Template(template_html)
    return t.render(**ctx)


__all__ = ["get_field_variables", "build_template_from_fields", "render_conditional_html"]
