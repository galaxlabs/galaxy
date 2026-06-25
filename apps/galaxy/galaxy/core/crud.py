import json
import secrets
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.engine import Engine

from galaxy.config import load_site_config
from galaxy.core.repository import get_doctype, get_doctype_fields
from galaxy.core.script_engine import run_scripts
from galaxy.core.tenant import current_tenant
from galaxy.db.connection import get_engine
from galaxy.db.core_tables import TENANT_TABLES


def _get_engine() -> Engine:
    _, site = load_site_config()
    return get_engine(site)


def _quote(name: str) -> str:
    return f'"{name}"'


SKIP_FIELDTYPES = {"Table"}


def _tenant_where(table_name: str) -> tuple[str, dict]:
    if table_name in TENANT_TABLES:
        return '"tenant_id" = :_tenant_id', {"_tenant_id": current_tenant.get() or "Default"}
    return "", {}


def get_doctype_for_crud(doctype_name: str) -> dict | None:
    doctype = get_doctype(doctype_name)
    if doctype is None:
        return None
    if doctype.get("migration_status") != "applied":
        return None
    return doctype


def get_crud_fields(doctype_name: str) -> list[dict]:
    return [f for f in get_doctype_fields(doctype_name) if f["fieldtype"] not in SKIP_FIELDTYPES and f["fieldname"] != "name"]


def validate_create_payload(doctype: dict, fields: list[dict], payload: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    cleaned: dict = {}
    valid_fieldnames = {f["fieldname"] for f in fields}
    required_fieldnames = {f["fieldname"] for f in fields if f.get("reqd")}
    hidden_readonly = {f["fieldname"] for f in fields if f.get("hidden") or f.get("read_only")}

    for key, val in payload.items():
        if key == "name":
            cleaned[key] = val
            continue
        if key not in valid_fieldnames:
            errors.append(f"Unknown field: '{key}'.")
            continue
        if key in hidden_readonly:
            errors.append(f"Field '{key}' is hidden or read-only and cannot be written directly.")
            continue
        cleaned[key] = val

    for req in required_fieldnames:
        if req not in cleaned or cleaned[req] is None or (isinstance(cleaned[req], str) and cleaned[req].strip() == ""):
            errors.append(f"Required field '{req}' is missing or empty.")

    return errors, cleaned


def _coerce_value(field: dict, value) -> tuple:
    ftype = field["fieldtype"]
    if ftype in ("Check",):
        return int(bool(value))
    if ftype in ("Int",):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid integer value for '{field['fieldname']}': {value!r}") from None
    if ftype in ("Float", "Currency"):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid number value for '{field['fieldname']}': {value!r}") from None
    if ftype in ("JSON",):
        if not isinstance(value, str):
            return json.dumps(value, ensure_ascii=False, default=str)
        return value
    return value


def _make_document_name(doctype_name: str) -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    rand = secrets.token_hex(2).upper()
    return f"{doctype_name}-{ts}-{rand}"


def create_document(doctype_name: str, payload: dict) -> dict:
    doctype = get_doctype_for_crud(doctype_name)
    if doctype is None:
        return {"success": False, "error": f"DocType '{doctype_name}' not found or migration not applied."}

    fields = get_crud_fields(doctype_name)
    errors, cleaned = validate_create_payload(doctype, fields, payload)
    if errors:
        return {"success": False, "error": "Validation failed.", "errors": errors}

    doc_name = cleaned.pop("name", None) or _make_document_name(doctype_name)
    table_name = doctype["table_name"]
    quoted_table = _quote(table_name)

    col_names = ["name"]
    col_values = [doc_name]

    if table_name in TENANT_TABLES:
        tenant_id = current_tenant.get() or "Default"
        col_names.append("tenant_id")
        col_values.append(tenant_id)

    for f in fields:
        fname = f["fieldname"]
        if fname not in cleaned:
            continue
        try:
            val = _coerce_value(f, cleaned[fname])
        except ValueError as e:
            return {"success": False, "error": str(e)}
        col_names.append(fname)
        col_values.append(val)

    placeholders = ", ".join(f":{c}" for c in col_names)
    quoted_cols = ", ".join(_quote(c) for c in col_names)

    sql = f"INSERT INTO {quoted_table} ({quoted_cols}) VALUES ({placeholders})"
    params = dict(zip(col_names, col_values, strict=True))

    from sqlalchemy.exc import IntegrityError

    engine = _get_engine()

    doc_data = {"doctype": doctype_name, "name": doc_name}
    for f in fields:
        if f["fieldname"] in col_names[1:]:
            doc_data[f["fieldname"]] = col_values[col_names.index(f["fieldname"])]

    script_errors = run_scripts(doctype_name, "before_save", doc_data)
    if script_errors:
        return {"success": False, "error": "Script validation failed.", "errors": script_errors}

    try:
        with engine.begin() as conn:
            conn.execute(text(sql), params)
    except IntegrityError:
        return {
            "success": False,
            "error": f"Document with name '{doc_name}' already exists.",
        }

    run_scripts(doctype_name, "after_save", doc_data)

    return {
        "success": True,
        "message": "Document created.",
        "data": {"doctype": doctype_name, "name": doc_name, "table_name": table_name},
    }


def list_documents(doctype_name: str, limit: int = 20, offset: int = 0) -> list[dict]:
    doctype = get_doctype_for_crud(doctype_name)
    if doctype is None:
        return {"success": False, "error": f"DocType '{doctype_name}' not found or migration not applied."}

    fields = get_crud_fields(doctype_name)
    table_name = doctype["table_name"]
    quoted_table = _quote(table_name)

    col_names = ["name"] + [f["fieldname"] for f in fields]
    quoted_cols = ", ".join(_quote(c) for c in col_names)

    tenant_clause, tenant_params = _tenant_where(table_name)
    where = f"WHERE {tenant_clause}" if tenant_clause else ""
    sql = f"SELECT {quoted_cols} FROM {quoted_table} {where} ORDER BY name LIMIT :lim OFFSET :off"

    engine = _get_engine()
    params = {"lim": limit, "off": offset}
    params.update(tenant_params)
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


def get_document(doctype_name: str, name: str) -> dict | None:
    doctype = get_doctype_for_crud(doctype_name)
    if doctype is None:
        return {"success": False, "error": f"DocType '{doctype_name}' not found or migration not applied."}

    fields = get_crud_fields(doctype_name)
    table_name = doctype["table_name"]
    quoted_table = _quote(table_name)

    col_names = ["name"] + [f["fieldname"] for f in fields]
    quoted_cols = ", ".join(_quote(c) for c in col_names)

    tenant_clause, tenant_params = _tenant_where(table_name)
    and_clause = f"AND {tenant_clause}" if tenant_clause else ""
    sql = f"SELECT {quoted_cols} FROM {quoted_table} WHERE name = :name {and_clause}"

    engine = _get_engine()
    params = {"name": name}
    params.update(tenant_params)
    with engine.connect() as conn:
        row = conn.execute(text(sql), params).mappings().one_or_none()
    if row is None:
        return None
    return dict(row)


def update_document(doctype_name: str, name: str, payload: dict) -> dict:
    doctype = get_doctype_for_crud(doctype_name)
    if doctype is None:
        return {"success": False, "error": f"DocType '{doctype_name}' not found or migration not applied."}

    existing = get_document(doctype_name, name)
    if existing is None:
        return {"success": False, "error": f"Document '{name}' not found."}

    fields = get_crud_fields(doctype_name)
    valid_fieldnames = {f["fieldname"] for f in fields}
    hidden_readonly = {f["fieldname"] for f in fields if f.get("hidden") or f.get("read_only")}
    errors: list[str] = []
    cleaned: dict = {}

    for key, val in payload.items():
        if key == "name":
            continue
        if key not in valid_fieldnames:
            errors.append(f"Unknown field: '{key}'.")
            continue
        if key in hidden_readonly:
            errors.append(f"Field '{key}' is hidden or read-only and cannot be written directly.")
            continue
        cleaned[key] = val

    if errors:
        return {"success": False, "error": "Validation failed.", "errors": errors}

    if not cleaned:
        return {"success": True, "message": "No changes.", "data": {"doctype": doctype_name, "name": name}}

    table_name = doctype["table_name"]
    quoted_table = _quote(table_name)
    set_parts: list[str] = []
    params: dict = {"name_param": name}

    for f in fields:
        fname = f["fieldname"]
        if fname not in cleaned:
            continue
        try:
            val = _coerce_value(f, cleaned[fname])
        except ValueError as e:
            return {"success": False, "error": str(e)}
        pname = f"p_{fname}"
        set_parts.append(f'{_quote(fname)} = :{pname}')
        params[pname] = val

    tenant_clause, extra_params = _tenant_where(table_name)
    and_clause = f"AND {tenant_clause}" if tenant_clause else ""
    sql = f"UPDATE {quoted_table} SET {', '.join(set_parts)} WHERE name = :name_param {and_clause}"
    params.update(extra_params)

    engine = _get_engine()

    doc_data = {"doctype": doctype_name, "name": name, **existing}
    doc_data.update(cleaned)

    script_errors = run_scripts(doctype_name, "before_save", doc_data)
    if script_errors:
        return {"success": False, "error": "Script validation failed.", "errors": script_errors}

    with engine.begin() as conn:
        conn.execute(text(sql), params)

    updated = get_document(doctype_name, name)
    run_scripts(doctype_name, "after_save", updated or doc_data)
    return {"success": True, "message": "Document updated.", "data": updated}


def delete_document(doctype_name: str, name: str) -> dict:
    doctype = get_doctype_for_crud(doctype_name)
    if doctype is None:
        return {"success": False, "error": f"DocType '{doctype_name}' not found or migration not applied."}

    existing = get_document(doctype_name, name)
    if existing is None:
        return {"success": False, "error": f"Document '{name}' not found."}

    table_name = doctype["table_name"]
    quoted_table = _quote(table_name)
    tenant_clause, extra_params = _tenant_where(table_name)
    and_clause = f"AND {tenant_clause}" if tenant_clause else ""
    sql = f'DELETE FROM {quoted_table} WHERE name = :name {and_clause}'

    engine = _get_engine()

    script_errors = run_scripts(doctype_name, "before_delete", existing)
    if script_errors:
        return {"success": False, "error": "Script validation failed.", "errors": script_errors}

    params = {"name": name}
    params.update(extra_params)
    with engine.begin() as conn:
        conn.execute(text(sql), params)

    run_scripts(doctype_name, "after_delete", {"doctype": doctype_name, "name": name, **existing})

    return {"success": True, "message": "Document deleted.", "data": {"doctype": doctype_name, "name": name}}
