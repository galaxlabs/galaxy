from apps.galaxy.galaxy.core.repository import get_doctype, get_doctype_fields, table_exists

PG_TYPE_MAP = {
    "Data": "TEXT",
    "Small Text": "TEXT",
    "Long Text": "TEXT",
    "Int": "INTEGER",
    "Float": "DOUBLE PRECISION",
    "Currency": "DOUBLE PRECISION",
    "Check": "SMALLINT",
    "Date": "DATE",
    "Datetime": "TIMESTAMP",
    "Select": "TEXT",
    "Link": "TEXT",
    "Attach": "TEXT",
    "JSON": "JSONB",
    "Code": "TEXT",
}


def map_fieldtype_to_sql(field: dict) -> str:
    ftype = field.get("fieldtype", "Data")
    return PG_TYPE_MAP.get(ftype, "TEXT")


def generate_create_table_plan(doctype: dict, fields: list[dict]) -> str:
    table_name = doctype["table_name"]
    lines = [f'CREATE TABLE "{table_name}" (']
    lines.append('    name TEXT PRIMARY KEY')

    for f in fields:
        ftype = f["fieldtype"]
        if ftype == "Table":
            continue
        col = f["fieldname"]
        sql_type = map_fieldtype_to_sql(f)
        not_null = " NOT NULL" if f.get("reqd") else ""
        lines.append(f'    , {col} {sql_type}{not_null}')

    lines.append(');')
    return "\n".join(lines) + "\n"


def plan_doctype_migration(doctype_name: str) -> dict:
    doctype = get_doctype(doctype_name)
    if doctype is None:
        return {"doctype_name": doctype_name, "exists": False, "plan": None}

    table_name = doctype["table_name"]
    already_applied = table_exists(table_name)
    fields = get_doctype_fields(doctype_name)

    if already_applied:
        return {
            "doctype_name": doctype_name,
            "exists": True,
            "table_name": table_name,
            "already_applied": True,
            "plan": None,
            "message": f"Table \"{table_name}\" already exists. No CREATE needed.",
        }

    sql = generate_create_table_plan(doctype, fields)
    return {
        "doctype_name": doctype_name,
        "exists": True,
        "table_name": table_name,
        "already_applied": False,
        "plan": {
            "operation": "create_table",
            "sql": sql,
        },
        "fields_count": len(fields),
        "message": f"CREATE TABLE plan generated for \"{table_name}\".",
    }
