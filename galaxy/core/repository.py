from sqlalchemy import text
from sqlalchemy.engine import Engine

from typing import TYPE_CHECKING

from galaxy.config import load_site_config
from galaxy.db.connection import get_engine

if TYPE_CHECKING:
    from galaxy.core.doctype.runtimemeta import RuntimeMeta


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


def get_custom_fields(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, fieldname, label, fieldtype, options,
                       reqd, hidden, read_only, in_list_view, in_standard_filter,
                       search_index, allow_on_submit, depends_on,
                       mandatory_depends_on, read_only_depends_on,
                       translatable, description, "default", enabled, idx
                FROM "tabCustomField" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_property_setters(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, property, value, field_name, property_type, enabled, idx
                FROM "tabPropertySetter" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_doctype_settings(doctype_name: str) -> dict:
    with _get_engine().connect() as conn:
        row = conn.execute(
            text("""
                SELECT name, parent, icon, icon_provider, color, theme,
                       default_view, max_attachments, allow_rename, allow_copy,
                       track_changes, track_seen, queue_documents, quick_entry,
                       sort_field, sort_order, search_fields, title_field,
                       image_field, enable_auto_repeat, document_type_class
                FROM "tabDocTypeSetting" WHERE parent = :name AND enabled = TRUE LIMIT 1
            """),
            {"name": doctype_name},
        ).mappings().one_or_none()
    return dict(row) if row else {}


def get_field_rules(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, field_name, rule_type, "value", condition, error_message, enabled, idx
                FROM "tabFieldRule" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_field_dependencies(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, field_name, depends_on_field, depends_on_value, action, enabled, idx
                FROM "tabFieldDependency" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_computed_fields(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, field_name, formula, fieldtype, options, script_type, enabled, idx
                FROM "tabComputedField" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_field_permissions(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, field_name, role, permlevel, "read", "write", enabled, idx
                FROM "tabFieldPermission" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_data_mask_rules(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, field_name, role, mask_type, mask_character,
                       unmasked_prefix_len, unmasked_suffix_len, condition, enabled, idx
                FROM "tabDataMaskRule" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_permission_rules(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, role, permlevel, "read", "write", "create", "delete",
                       "select", "amend", "condition", apply_to_child, enabled, idx
                FROM "tabPermissionRule" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_display_logic(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, field_name, depends_on_field, operator, "value",
                       action, condition_group, priority, enabled, idx
                FROM "tabDisplayLogic" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def get_dynamic_sources(doctype_name: str) -> list[dict]:
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT name, parent, field_name, source_type, source_handler,
                       filters, depends_on, cache_ttl, permission_required, enabled, idx
                FROM "tabDynamicFieldSource" WHERE parent = :name AND enabled = TRUE ORDER BY idx
            """),
            {"name": doctype_name},
        ).mappings().all()
    return [dict(r) for r in rows]


def clear_meta_cache(doctype_name: str | None = None) -> None:
    from galaxy.core.doctype.meta_cache import meta_cache
    if doctype_name:
        meta_cache.invalidate_doctype(doctype_name)
    else:
        meta_cache.invalidate()


def get_runtime_meta(doctype_name: str) -> RuntimeMeta | None:
    from galaxy.core.doctype.meta_cache import meta_cache
    from galaxy.core.doctype.runtimemeta import merge_meta

    cached = meta_cache.get(doctype_name)
    if cached is not None:
        return cached

    doctype = get_doctype(doctype_name)
    if doctype is None:
        return None

    base_fields = get_doctype_fields(doctype_name)
    permissions = get_doctype_permissions(doctype_name)
    custom_fields = get_custom_fields(doctype_name)
    property_setters = get_property_setters(doctype_name)
    settings = get_doctype_settings(doctype_name)
    field_rules = get_field_rules(doctype_name)
    field_dependencies = get_field_dependencies(doctype_name)
    computed_fields = get_computed_fields(doctype_name)
    field_permissions = get_field_permissions(doctype_name)
    data_mask_rules = get_data_mask_rules(doctype_name)
    permission_rules = get_permission_rules(doctype_name)
    display_logic = get_display_logic(doctype_name)
    dynamic_sources = get_dynamic_sources(doctype_name)

    meta = merge_meta(
        doctype, base_fields, permissions,
        custom_fields=custom_fields,
        property_setters=property_setters,
        settings=settings,
        field_rules=field_rules,
        field_dependencies=field_dependencies,
        computed_fields=computed_fields,
        field_permissions=field_permissions,
        data_mask_rules=data_mask_rules,
        permission_rules=permission_rules,
        display_logic=display_logic,
        dynamic_sources=dynamic_sources,
    )
    if meta is not None:
        meta_cache.set(doctype_name, meta)
    return meta


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
