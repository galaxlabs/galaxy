from sqlalchemy import text
from sqlalchemy.engine import Engine

from internal.config.site_config import load_site_config
from internal.db.connection import get_engine


def _get_engine() -> Engine:
    _, site = load_site_config()
    return get_engine(site)


def table_exists(table_name: str) -> bool:
    with _get_engine().connect() as conn:
        row = conn.execute(
            text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = :name
            """),
            {"name": table_name},
        ).scalar()
    return row > 0


def _migration_status(table_name: str) -> str:
    return "applied" if table_exists(table_name) else "pending"


def _enrich(dt: dict) -> dict:
    dt["migration_status"] = _migration_status(dt["table_name"])
    return dt


def get_installed_apps():
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text('SELECT name, app_name, app_version, enabled, idx FROM "tabInstalled App" ORDER BY idx')
        ).mappings().all()
    return [dict(r) for r in rows]


def get_installed_modules():
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text('SELECT name, module_name, app_name, enabled, idx FROM "tabInstalled Module" ORDER BY idx')
        ).mappings().all()
    return [dict(r) for r in rows]


def get_modules():
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text('SELECT name, module_name, app_name, label, description, enabled, idx FROM "tabModule Def" ORDER BY idx')
        ).mappings().all()
    return [dict(r) for r in rows]


def get_doctypes():
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, module, app_name, table_name,
                       is_single, is_submittable, is_child_table, is_tree, idx
                FROM "tabDocType" ORDER BY idx
            """)
        ).mappings().all()
    return [_enrich(dict(r)) for r in rows]


def get_doctype(name: str):
    with _get_engine().connect() as conn:
        row = conn.execute(
            text("""
                SELECT name, module, app_name, table_name,
                       is_single, is_submittable, is_child_table, is_tree, idx
                FROM "tabDocType" WHERE name = :name
            """),
            {"name": name},
        ).mappings().one_or_none()
    if row is None:
        return None
    return _enrich(dict(row))


def get_doctype_fields(name: str):
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT fieldname, label, fieldtype, options,
                       reqd, hidden, read_only, in_list_view, idx
                FROM "tabDocField" WHERE parent = :name ORDER BY idx
            """),
            {"name": name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_doctype_permissions(name: str):
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT role, permlevel, "read", "write", "create", "delete", idx
                FROM "tabDocPerm" WHERE parent = :name ORDER BY idx
            """),
            {"name": name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_core_summary():
    with _get_engine().connect() as conn:
        installed_apps = conn.execute(text('SELECT COUNT(*) FROM "tabInstalled App"')).scalar()
        installed_modules = conn.execute(text('SELECT COUNT(*) FROM "tabInstalled Module"')).scalar()
        modules = conn.execute(text('SELECT COUNT(*) FROM "tabModule Def"')).scalar()
        doctypes = conn.execute(text('SELECT COUNT(*) FROM "tabDocType"')).scalar()
        docfields = conn.execute(text('SELECT COUNT(*) FROM "tabDocField"')).scalar()
        docperms = conn.execute(text('SELECT COUNT(*) FROM "tabDocPerm"')).scalar()
        users = conn.execute(text('SELECT COUNT(*) FROM "tabUser"')).scalar()
        roles = conn.execute(text('SELECT COUNT(*) FROM "tabRole"')).scalar()
    return {
        "installed_apps": installed_apps,
        "installed_modules": installed_modules,
        "modules": modules,
        "doctypes": doctypes,
        "docfields": docfields,
        "docperms": docperms,
        "users": users,
        "roles": roles,
    }
