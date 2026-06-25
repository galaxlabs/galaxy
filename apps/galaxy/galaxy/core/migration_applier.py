from sqlalchemy import text
from sqlalchemy.engine import Engine

from apps.galaxy.galaxy.core.migration_planner import plan_doctype_migration
from apps.galaxy.galaxy.core.repository import table_exists
from galaxy.db.connection import get_engine
from internal.config.site_config import load_site_config


def _get_engine() -> Engine:
    _, site = load_site_config()
    return get_engine(site)


def apply_doctype_migration(doctype_name: str) -> dict:
    plan = plan_doctype_migration(doctype_name)

    if not plan["exists"]:
        return {"success": False, "message": "DocType not found."}

    if plan["already_applied"]:
        return {"success": False, "message": "Migration already applied."}

    if plan.get("plan") is None:
        return {"success": False, "message": "No migration plan available."}

    operation = plan["plan"].get("operation")
    if operation != "create_table":
        return {"success": False, "message": f"Unsupported operation: {operation}"}

    sql = plan["plan"]["sql"]

    engine = _get_engine()
    with engine.begin() as conn:
        conn.execute(text(sql))

    table_name = plan["table_name"]
    exists = table_exists(table_name)

    if not exists:
        return {"success": False, "message": "Migration execution failed — table not created."}

    return {
        "success": True,
        "message": "Migration applied.",
        "data": {
            "doctype": doctype_name,
            "table_name": table_name,
            "operation": operation,
            "table_exists": exists,
        },
    }
