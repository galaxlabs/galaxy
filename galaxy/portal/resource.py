from starlette.responses import JSONResponse

from galaxy.model.document import (
    create_document as _create_document,
    get_document as _get_document,
    list_documents as _list_documents,
    update_document as _update_document,
    delete_document as _delete_document,
)
from galaxy.portal.auth import portal_require_session
from galaxy.portal.permissions import PortalPermissionEngine


def _get_session(request) -> tuple[dict | None, PortalPermissionEngine | None]:
    session = portal_require_session(request)
    if session is None:
        return None, None
    engine = PortalPermissionEngine(session["email"], session["portal_role"])
    return session, engine


def _filter_readable(result: dict | None, engine: PortalPermissionEngine, doctype: str):
    if result is None:
        return None
    readable = engine.get_readable_fields(doctype)
    if readable is None:
        return result
    if isinstance(result, dict):
        return {k: v for k, v in result.items() if k in readable or k in ("name", "doctype")}
    return result


def _filter_writable(payload: dict, engine: PortalPermissionEngine, doctype: str) -> dict:
    writable = engine.get_writable_fields(doctype)
    if not writable:
        return {}
    return {k: v for k, v in payload.items() if k in writable}


async def portal_create(request):
    session, perm = _get_session(request)
    if session is None:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)
    doctype = request.path_params.get("doctype", "")
    if not perm.can_create(doctype) and not perm.can_write(doctype):
        return JSONResponse({"error": "Permission denied."}, status_code=403)
    body = await request.json()
    filtered = _filter_writable(body, perm, doctype) if perm.get_readable_fields(doctype) is not None else body
    result = _create_document(doctype, filtered)
    if result.get("success"):
        return JSONResponse(result, status_code=201)
    return JSONResponse(result, status_code=400)


async def portal_list(request):
    session, perm = _get_session(request)
    if session is None:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)
    doctype = request.path_params.get("doctype", "")
    if not perm.can_read(doctype):
        return JSONResponse({"error": "Permission denied."}, status_code=403)
    owned = perm.get_owned_docs(doctype)
    docnames = [d["docname"] for d in owned]
    if not docnames:
        return JSONResponse({"data": []})
    from galaxy.model.repository import get_doctype
    from galaxy.model.document import get_crud_fields, _quote

    dt = get_doctype(doctype)
    if dt is None:
        return JSONResponse({"error": "DocType not found."}, status_code=404)
    fields = get_crud_fields(doctype)
    table_name = dt.get("table_name", f"tab{doctype}")
    quoted_table = _quote(table_name)

    col_names = ["name"] + [f["fieldname"] for f in fields]
    quoted_cols = ", ".join(_quote(c) for c in col_names)
    placeholders = ", ".join(f":d{i}" for i in range(len(docnames)))
    params = {f"d{i}": n for i, n in enumerate(docnames)}
    sql = f"SELECT {quoted_cols} FROM {quoted_table} WHERE name IN ({placeholders}) ORDER BY name"

    from galaxy.config import load_site_config
    from galaxy.database.connection import get_engine
    from sqlalchemy import text

    _, site = load_site_config()
    engine = get_engine(site)
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    results = [dict(r) for r in rows]
    results = [_filter_readable(r, perm, doctype) for r in results]
    return JSONResponse({"data": results})


async def portal_get(request):
    session, perm = _get_session(request)
    if session is None:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)
    doctype = request.path_params.get("doctype", "")
    docname = request.path_params.get("docname", "")
    if not perm.can_read(doctype):
        return JSONResponse({"error": "Permission denied."}, status_code=403)
    if not perm.can_access_doc(doctype, docname):
        return JSONResponse({"error": "Not found."}, status_code=404)
    result = _get_document(doctype, docname)
    if result is None:
        return JSONResponse({"error": "Not found."}, status_code=404)
    result = _filter_readable(result, perm, doctype)
    return JSONResponse({"data": result})


async def portal_update(request):
    session, perm = _get_session(request)
    if session is None:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)
    doctype = request.path_params.get("doctype", "")
    docname = request.path_params.get("docname", "")
    if not perm.can_write(doctype):
        return JSONResponse({"error": "Permission denied."}, status_code=403)
    if not perm.can_access_doc(doctype, docname):
        return JSONResponse({"error": "Not found."}, status_code=404)
    body = await request.json()
    filtered = _filter_writable(body, perm, doctype) if perm.get_readable_fields(doctype) is not None else body
    result = _update_document(doctype, docname, filtered)
    if result.get("success"):
        return JSONResponse(result)
    return JSONResponse(result, status_code=400)


async def portal_delete(request):
    session, perm = _get_session(request)
    if session is None:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)
    doctype = request.path_params.get("doctype", "")
    docname = request.path_params.get("docname", "")
    if not perm.can_delete(doctype):
        return JSONResponse({"error": "Permission denied."}, status_code=403)
    if not perm.can_access_doc(doctype, docname):
        return JSONResponse({"error": "Not found."}, status_code=404)
    result = _delete_document(doctype, docname)
    if result.get("success"):
        return JSONResponse(result)
    return JSONResponse(result, status_code=400)


__all__ = [
    "portal_create",
    "portal_list",
    "portal_get",
    "portal_update",
    "portal_delete",
]
