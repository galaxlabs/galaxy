import traceback
from datetime import UTC

from sqlalchemy import text

from internal.config.site_config import load_site_config
from internal.db.connection import get_engine

VALID_EVENTS = {"before_save", "after_save", "before_delete", "after_delete", "on_load"}


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


class FrappeDB:
    def __init__(self, engine):
        self._engine = engine

    def sql(self, query: str, params: dict | None = None):
        with self._engine.connect() as conn:
            rows = conn.execute(text(query), params or {}).mappings().all()
        return [dict(r) for r in rows]

    def get_value(self, table: str, field: str, filters: dict) -> str | None:
        where_clause = " AND ".join(f'"{k}" = :{k}' for k in filters)
        sql_str = f'SELECT "{field}" FROM "{table}" WHERE {where_clause} LIMIT 1'
        with self._engine.connect() as conn:
            row = conn.execute(text(sql_str), filters).mappings().one_or_none()
        if row is None:
            return None
        return row[field]


class FrappeAPI:
    def __init__(self, engine):
        self.db = FrappeDB(engine)
        self._engine = engine

    def get_doc(self, doctype: str, name: str) -> dict | None:
        from internal.core.crud import get_document as _get_doc
        return _get_doc(doctype, name)

    def log_error(self, message: str):
        try:
            with self._engine.begin() as conn:
                from datetime import datetime
                ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
                conn.execute(
                    text('INSERT INTO "tabError Log" (name, message, source, user_name, status) VALUES (:name, :message, :source, :user_name, :status)'),
                    {"name": f"Script-{ts}", "message": message, "source": "server_script", "user_name": "System", "status": "Error"},
                )
        except Exception:
            pass


def get_scripts_for_event(doctype_name: str, event: str) -> list[dict]:
    if event not in VALID_EVENTS:
        return []
    engine = _get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, script, script_type
                FROM "tabServer Script"
                WHERE ref_doctype = :dt AND doctype_event = :ev AND enabled = TRUE
                ORDER BY idx
            """),
            {"dt": doctype_name, "ev": event},
        ).mappings().all()
    return [dict(r) for r in rows]


def run_scripts(doctype_name: str, event: str, doc: dict) -> list[str]:
    errors: list[str] = []

    from internal.core.security import get_security_settings, log_security_event

    sec = get_security_settings()
    if not sec["allow_server_scripts"]:
        log_security_event("script_blocked", None, f"Server scripts disabled. Blocked {event} on {doctype_name}.", "server_script")
        return errors

    scripts = get_scripts_for_event(doctype_name, event)
    if not scripts:
        return errors

    engine = _get_engine()
    frappe = FrappeAPI(engine)

    for script_def in scripts:
        if script_def["script_type"] != "Python":
            continue
        code = script_def["script"]
        if not code:
            continue
        globals_dict = {
            "doc": doc,
            "frappe": frappe,
        }
        try:
            exec(code, globals_dict)
        except Exception as e:
            tb = traceback.format_exc()
            msg = f"Script '{script_def['name']}' failed on {event}: {e}"
            errors.append(msg)
            frappe.log_error(f"{msg}\n{tb}")

    return errors
