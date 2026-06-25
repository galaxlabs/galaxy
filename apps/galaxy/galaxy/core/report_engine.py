import json
import traceback

from sqlalchemy import text

from galaxy.config import load_site_config
from galaxy.core.security import get_security_settings, log_security_event
from galaxy.db.connection import get_engine


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


def get_report(name: str) -> dict | None:
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT name, ref_doctype, report_type, query, script, columns, enabled
                FROM "tabReport" WHERE name = :name
            """),
            {"name": name},
        ).mappings().one_or_none()
    if row is None:
        return None
    result = dict(row)
    if result.get("columns"):
        try:
            result["columns"] = json.loads(result["columns"])
        except Exception:
            pass
    return result


DANGEROUS_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter", "create",
    "truncate", "grant", "revoke", "copy", "call", "do",
    "replace", "rename", "comment", "merge",
]

COMMENT_PATTERNS = ["--", "/*", "*/", "#"]


def _validate_query_safe(query: str) -> tuple[bool, str]:
    stripped = query.strip().rstrip(";")
    if not stripped:
        return False, "Query is empty."

    semi_count = stripped.count(";")
    if semi_count > 0:
        return False, "Multiple statements are not allowed (semicolon detected)."

    import re
    no_comments = stripped
    for pat in COMMENT_PATTERNS:
        no_comments = re.sub(re.escape(pat) + ".*", "", no_comments)

    lower = no_comments.lower().strip()
    if not lower.startswith("select") and not lower.startswith("with"):
        return False, "Only SELECT queries are allowed."

    words = set(lower.split())
    for kw in DANGEROUS_KEYWORDS:
        if kw in words:
            return False, f"Dangerous keyword '{kw}' is not allowed."

    return True, ""


def run_query_report(report: dict) -> dict:
    query = (report.get("query") or "").strip()
    if not query:
        return {"success": False, "error": "Query is empty."}

    valid, msg = _validate_query_safe(query)
    if not valid:
        return {"success": False, "error": msg}

    try:
        engine = _get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text(query)).mappings().all()
        result = [dict(r) for r in rows]
    except Exception:
        log_security_event("query_report_error", None, f"Query report execution failed for query: {query[:200]}", "report")
        return {"success": False, "error": "Query report execution failed."}

    return {"success": True, "data": result, "count": len(result)}


def run_script_report(report: dict) -> dict:
    script = (report.get("script") or "").strip()
    if not script:
        return {"success": False, "error": "Script is empty."}

    engine = _get_engine()
    globals_dict = {"engine": engine, "frappe_db": None}
    from galaxy.core.script_engine import FrappeDB

    globals_dict["frappe_db"] = FrappeDB(engine)

    try:
        exec(script, globals_dict)
        result = globals_dict.get("result", [])
        if not isinstance(result, list):
            result = [result]
    except Exception as e:
        tb = traceback.format_exc()
        log_security_event("script_report_error", None, f"Script report execution failed: {e}\n{tb}", "report")
        return {"success": False, "error": "Script report execution failed."}

    return {"success": True, "data": result, "count": len(result)}


def run_report(name: str) -> dict:
    report = get_report(name)
    if report is None:
        return {"success": False, "error": f"Report '{name}' not found."}
    if not report.get("enabled"):
        return {"success": False, "error": f"Report '{name}' is disabled."}

    rtype = report.get("report_type", "Query Report")
    sec = get_security_settings()

    if rtype == "Query Report":
        if not sec["allow_query_reports"]:
            log_security_event("query_report_blocked", None, f"Query reports disabled. Blocked report '{name}'.", "report")
            return {"success": False, "error": "Query reports are disabled by the system administrator."}
        return run_query_report(report)
    elif rtype == "Script Report":
        if not sec["allow_script_reports"]:
            log_security_event("script_report_blocked", None, f"Script reports disabled. Blocked report '{name}'.", "report")
            return {"success": False, "error": "Script reports are disabled by the system administrator."}
        return run_script_report(report)
    else:
        return {"success": False, "error": f"Unknown report type: {rtype}"}
