from sqlalchemy import text
from sqlalchemy.engine import Engine

from galaxy.core.builder import build_doctype_json, validate_doctype_payload
from galaxy.db.connection import get_engine
from internal.config.site_config import load_site_config


def _get_engine() -> Engine:
    _, site = load_site_config()
    return get_engine(site)


def save_doctype_metadata(payload: dict) -> dict:
    errors, warnings = validate_doctype_payload(payload)
    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}

    result = build_doctype_json(payload)
    dt = result["doctype"]
    fields = result["fields"]

    engine = _get_engine()

    with engine.begin() as conn:
        existing = conn.execute(
            text('SELECT COUNT(*) FROM "tabDocType" WHERE name = :name'),
            {"name": dt["name"]},
        ).scalar()

        if existing:
            conn.execute(
                text("""
                    UPDATE "tabDocType"
                    SET module = :module, app_name = :app_name, table_name = :table_name,
                        is_single = :is_single, is_submittable = :is_submittable,
                        is_child_table = :is_child_table, is_tree = :is_tree,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE name = :name
                """),
                {
                    "name": dt["name"],
                    "module": dt["module"],
                    "app_name": dt["app_name"],
                    "table_name": dt["table_name"],
                    "is_single": dt["is_single"],
                    "is_submittable": dt["is_submittable"],
                    "is_child_table": dt["is_child_table"],
                    "is_tree": dt["is_tree"],
                },
            )
        else:
            existing_idx = conn.execute(text('SELECT COALESCE(MAX(idx), -1) + 1 FROM "tabDocType"')).scalar()
            conn.execute(
                text("""
                    INSERT INTO "tabDocType"
                    (name, module, app_name, table_name, is_single, is_submittable, is_child_table, is_tree, idx)
                    VALUES (:name, :module, :app_name, :table_name, :is_single, :is_submittable, :is_child_table, :is_tree, :idx)
                """),
                {
                    "name": dt["name"],
                    "module": dt["module"],
                    "app_name": dt["app_name"],
                    "table_name": dt["table_name"],
                    "is_single": dt["is_single"],
                    "is_submittable": dt["is_submittable"],
                    "is_child_table": dt["is_child_table"],
                    "is_tree": dt["is_tree"],
                    "idx": existing_idx,
                },
            )

        conn.execute(
            text('DELETE FROM "tabDocField" WHERE parent = :parent'),
            {"parent": dt["name"]},
        )

        for f in fields:
            conn.execute(
                text("""
                    INSERT INTO "tabDocField"
                    (name, parent, fieldname, label, fieldtype, options, reqd, hidden, read_only, in_list_view, idx)
                    VALUES (:name, :parent, :fieldname, :label, :fieldtype, :options, :reqd, :hidden, :read_only, :in_list_view, :idx)
                """),
                {
                    "name": f["name"],
                    "parent": f["parent"],
                    "fieldname": f["fieldname"],
                    "label": f["label"],
                    "fieldtype": f["fieldtype"],
                    "options": f["options"],
                    "reqd": f["reqd"],
                    "hidden": f["hidden"],
                    "read_only": f["read_only"],
                    "in_list_view": f["in_list_view"],
                    "idx": f["idx"],
                },
            )

    return {
        "valid": True,
        "message": "DocType metadata saved.",
        "data": result,
    }
