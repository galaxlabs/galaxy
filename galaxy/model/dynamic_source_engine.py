from galaxy.model.runtimemeta import RuntimeMeta


def resolve_field_options(
    meta: RuntimeMeta,
    field_name: str,
    doc_data: dict,
    role: str | None = None,
) -> list:
    sources = meta.dynamic_sources.get(field_name, [])
    if not sources:
        return []

    for source in sources:
        if not source.get("enabled", True):
            continue
        perm = source.get("permission_required", "")
        if perm and role != perm:
            continue
        deps = source.get("depends_on")
        if deps is not None and not _check_dependencies(deps, doc_data):
            continue
        return _resolve_source(source, doc_data)

    return []


def resolve_all_field_options(
    meta: RuntimeMeta,
    doc_data: dict,
    role: str | None = None,
) -> dict[str, list]:
    results: dict[str, list] = {}
    for field_name in meta.dynamic_sources:
        opts = resolve_field_options(meta, field_name, doc_data, role)
        if opts:
            results[field_name] = opts
    return results


def _check_dependencies(depends_on, doc_data: dict) -> bool:
    if isinstance(depends_on, str):
        import json
        try:
            depends_on = json.loads(depends_on)
        except (json.JSONDecodeError, TypeError):
            return True
    if not isinstance(depends_on, dict):
        return True
    for field, expected in depends_on.items():
        actual = doc_data.get(field)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def _resolve_source(source: dict, doc_data: dict) -> list:
    source_type = source.get("source_type", "static")
    handler = source.get("source_handler", "")
    filters_raw = source.get("filters")

    if source_type == "static":
        return _resolve_static(handler)
    if source_type == "query":
        return _resolve_query(handler, doc_data)
    if source_type == "document":
        return _resolve_document(handler, filters_raw)
    if source_type == "script":
        return _resolve_script(handler, doc_data)
    if source_type == "api":
        return _resolve_api(handler, filters_raw)
    if source_type == "user_context":
        return _resolve_user_context(handler)
    return []


def _resolve_static(handler: str) -> list:
    if not handler:
        return []
    return [{"value": v.strip(), "label": v.strip()} for v in handler.split("\n") if v.strip()]


def _resolve_query(handler: str, doc_data: dict) -> list:
    if not handler:
        return []
    from galaxy.config import load_site_config
    from galaxy.database.connection import get_engine
    from sqlalchemy import text

    import re

    _, site = load_site_config()
    engine = get_engine(site)

    def _replace_field(m):
        return str(doc_data.get(m.group(1), ""))

    query = re.sub(r"\{(\w+)\}", _replace_field, handler)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(query)).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


def _resolve_document(handler: str, filters_raw) -> list:
    if not handler:
        return []
    from galaxy.model.document import list_documents

    try:
        result = list_documents(handler, limit=100)
        if isinstance(result, list):
            return [{"value": r["name"], "label": r.get("title", r["name"])} for r in result]
        return []
    except Exception:
        return []


def _resolve_script(handler: str, doc_data: dict) -> list:
    if not handler:
        return []
    from galaxy.model.field_rule_engine import _safe_eval

    ctx = {**doc_data, "doc": doc_data}
    result = _safe_eval(handler, ctx)
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return [{"value": k, "label": v} for k, v in result.items()]
    return []


def _resolve_api(handler: str, filters_raw) -> list:
    if not handler:
        return []
    import json
    import urllib.request

    try:
        with urllib.request.urlopen(handler, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return []
    except Exception:
        return []


def _resolve_user_context(handler: str) -> list:
    if not handler:
        return []
    return [{"value": handler, "label": handler}]
