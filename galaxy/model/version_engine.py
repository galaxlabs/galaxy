import json
import secrets
from datetime import UTC, datetime

from sqlalchemy import text

from galaxy.config import load_site_config
from galaxy.database.connection import get_engine
from galaxy.model.repository import get_doctype


def _get_engine():
    _, site = load_site_config()
    return get_engine(site)


def should_track_changes(doctype: str) -> bool:
    dt = get_doctype(doctype)
    return bool(dt and dt.get("track_changes"))


def get_field_delta(old_doc: dict, new_doc: dict) -> dict:
    delta = {}
    all_keys = set(old_doc.keys()) | set(new_doc.keys())
    for key in all_keys:
        old_val = old_doc.get(key)
        new_val = new_doc.get(key)
        if old_val != new_val:
            delta[key] = {"old": old_val, "new": new_val}
    return delta


def create_version(doctype: str, docname: str, doc_data: dict, changed_fields: dict | None = None, comment: str = "", user: str = "") -> dict | None:
    if not should_track_changes(doctype):
        return None
    engine = _get_engine()
    name = f"ver-{secrets.token_hex(8)}"
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabDocVersion"
                (name, ref_doctype, docname, version_data, changed_fields, comment, created_by, idx, created_at)
                VALUES (:name, :ref_doctype, :docname, :version_data, :changed_fields, :comment, :created_by, 0, CURRENT_TIMESTAMP)
            """),
            {
                "name": name,
                "ref_doctype": doctype,
                "docname": docname,
                "version_data": json.dumps(doc_data, ensure_ascii=False, default=str),
                "changed_fields": json.dumps(changed_fields or {}, ensure_ascii=False, default=str),
                "comment": comment,
                "created_by": user,
            },
        )
    return {"name": name, "ref_doctype": doctype, "docname": docname}


def get_versions(doctype: str, docname: str, limit: int = 20) -> list[dict]:
    engine = _get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, ref_doctype, docname, version_data, changed_fields, comment, created_by, created_at
                FROM "tabDocVersion"
                WHERE ref_doctype = :doctype AND docname = :docname
                ORDER BY created_at DESC LIMIT :lim
            """),
            {"doctype": doctype, "docname": docname, "lim": limit},
        ).mappings().all()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["version_data"] = json.loads(d["version_data"]) if isinstance(d["version_data"], str) else d["version_data"]
        except (json.JSONDecodeError, TypeError):
            pass
        try:
            d["changed_fields"] = json.loads(d["changed_fields"]) if isinstance(d["changed_fields"], str) else d["changed_fields"]
        except (json.JSONDecodeError, TypeError):
            pass
        result.append(d)
    return result


__all__ = ["create_version", "get_versions", "should_track_changes", "get_field_delta"]
