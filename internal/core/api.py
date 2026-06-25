import urllib.parse

from sqlalchemy import text
from starlette.responses import JSONResponse

from internal.config.site_config import load_site_config
from internal.core.auth import create_session, delete_session, get_session, verify_password
from internal.core.builder import build_doctype_json, validate_doctype_payload
from internal.core.builder_repository import save_doctype_metadata
from internal.core.crud import create_document, delete_document, get_document, list_documents, update_document
from internal.core.migration_applier import apply_doctype_migration
from internal.core.migration_planner import plan_doctype_migration
from internal.core.permissions import authorize
from internal.core.report_engine import run_report
from internal.core.repository import (
    get_core_summary,
    get_doctype,
    get_doctype_fields,
    get_doctype_permissions,
    get_doctypes,
    get_installed_apps,
    get_installed_modules,
    get_modules,
)
from internal.db.connection import get_engine


async def handle_installed_apps(request):
    try:
        data = get_installed_apps()
        return JSONResponse({"data": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_installed_modules(request):
    try:
        data = get_installed_modules()
        return JSONResponse({"data": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_modules(request):
    try:
        data = get_modules()
        return JSONResponse({"data": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_doctypes(request):
    try:
        data = get_doctypes()
        return JSONResponse({"data": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_doctype(request):
    name = request.path_params.get("name")
    try:
        data = get_doctype(name)
        if data is None:
            return JSONResponse({"error": "DocType not found"}, status_code=404)
        return JSONResponse({"data": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_doctype_fields(request):
    name = request.path_params.get("name")
    try:
        doctype = get_doctype(name)
        if doctype is None:
            return JSONResponse({"error": "DocType not found"}, status_code=404)
        data = get_doctype_fields(name)
        return JSONResponse({"doctype": name, "data": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_doctype_permissions(request):
    name = request.path_params.get("name")
    try:
        doctype = get_doctype(name)
        if doctype is None:
            return JSONResponse({"error": "DocType not found"}, status_code=404)
        data = get_doctype_permissions(name)
        return JSONResponse({"doctype": name, "data": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_summary(request):
    try:
        data = get_core_summary()
        return JSONResponse({"data": data})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_builder_preview(request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

    errors, warnings = validate_doctype_payload(payload)
    if errors:
        return JSONResponse({"valid": False, "errors": errors, "warnings": warnings}, status_code=400)

    result = build_doctype_json(payload)
    return JSONResponse({
        "valid": True,
        "warnings": warnings,
        "preview": result,
    })


async def handle_builder_save(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

    try:
        result = save_doctype_metadata(payload)
    except Exception as e:
        return JSONResponse({"error": f"Save failed: {e!s}"}, status_code=500)

    if not result.get("valid"):
        return JSONResponse(result, status_code=400)

    return JSONResponse(result)


async def handle_migration_preview(request):
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    try:
        result = plan_doctype_migration(name)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    if not result["exists"]:
        return JSONResponse({"error": "DocType not found"}, status_code=404)

    return JSONResponse({"data": result})


async def handle_migration_apply(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    try:
        result = apply_doctype_migration(name)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    if not result["success"] and result["message"] == "DocType not found.":
        return JSONResponse({"error": result["message"]}, status_code=404)

    if not result["success"] and result["message"] == "Migration already applied.":
        return JSONResponse(result, status_code=409)

    if not result["success"]:
        return JSONResponse(result, status_code=400)

    return JSONResponse(result)


def _get_user(request):
    cookie = request.cookies.get("galaxy_session")
    if cookie:
        session = get_session(cookie)
        if session:
            return session["username"]
    return request.headers.get("X-Galaxy-User", "Administrator")


def require_auth(request) -> str | None:
    cookie = request.cookies.get("galaxy_session")
    if not cookie:
        return None
    session = get_session(cookie)
    if session is None:
        return None
    return session["username"]


AUTH_REQUIRED = {"success": False, "error": "Authentication required."}


def _err(status: int, error: str, errors: list[str] | None = None):
    body: dict = {"success": False, "error": error}
    if errors:
        body["errors"] = errors
    return JSONResponse(body, status_code=status)


def _ok(data, status: int = 200):
    return JSONResponse({"success": True, "data": data}, status_code=status)


async def handle_login(request):
    try:
        payload = await request.json()
    except Exception:
        return _err(400, "Invalid JSON body.")

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return _err(400, "Username and password are required.")

    user = verify_password(username, password)
    if user is None:
        return _err(401, "Invalid username or password.")

    token = create_session(username)
    response = _ok({"user": user, "token": token})
    response.set_cookie(
        key="galaxy_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400,
        path="/",
    )
    return response


async def handle_logout(request):
    cookie = request.cookies.get("galaxy_session")
    if cookie:
        delete_session(cookie)
    response = _ok({"message": "Logged out."})
    response.set_cookie(
        key="galaxy_session",
        value="",
        httponly=True,
        samesite="lax",
        max_age=0,
        path="/",
    )
    return response


async def handle_auth_me(request):
    cookie = request.cookies.get("galaxy_session")
    if not cookie:
        return _err(401, "Not authenticated.")

    user = get_session(cookie)
    if user is None:
        response = _err(401, "Session expired or invalid.")
        response.set_cookie(
            key="galaxy_session",
            value="",
            httponly=True,
            samesite="lax",
            max_age=0,
            path="/",
        )
        return response

    return _ok({"user": user})


async def handle_resource_create(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    raw = request.path_params.get("doctype", "")
    doctype = urllib.parse.unquote(raw)
    user = _get_user(request)
    ok, msg = authorize(doctype, user, "create")
    if not ok:
        return _err(403, msg)

    try:
        payload = await request.json()
    except Exception:
        return _err(400, "Invalid JSON body.")

    if not isinstance(payload, dict):
        return _err(400, "Request body must be a JSON object.")

    try:
        result = create_document(doctype, payload)
    except Exception as e:
        return _err(500, str(e))

    if not result["success"]:
        err_msg = result.get("error", "Error")
        is_not_found = "not found" in err_msg.lower() or "not applied" in err_msg.lower()
        is_dup = "already exists" in err_msg.lower()
        if is_not_found:
            return _err(404, err_msg)
        if is_dup:
            return _err(409, err_msg)
        return _err(400, err_msg, result.get("errors"))

    return _ok(result["data"], 201)


async def handle_resource_list(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    raw = request.path_params.get("doctype", "")
    doctype = urllib.parse.unquote(raw)
    user = _get_user(request)
    ok, msg = authorize(doctype, user, "read")
    if not ok:
        return _err(403, msg)

    try:
        limit = int(request.query_params.get("limit", 20))
    except Exception:
        limit = 20
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100

    try:
        offset = int(request.query_params.get("offset", 0))
    except Exception:
        offset = 0
    if offset < 0:
        offset = 0

    try:
        result = list_documents(doctype, limit=limit, offset=offset)
    except Exception as e:
        return _err(500, str(e))

    if isinstance(result, dict) and not result.get("success", True):
        return _err(404, result.get("error", "Not found"))

    return _ok({"items": result, "limit": limit, "offset": offset})


async def handle_resource_get(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    raw_dt = request.path_params.get("doctype", "")
    raw_name = request.path_params.get("name", "")
    doctype = urllib.parse.unquote(raw_dt)
    name = urllib.parse.unquote(raw_name)
    user = _get_user(request)
    ok, msg = authorize(doctype, user, "read")
    if not ok:
        return _err(403, msg)

    try:
        doc = get_document(doctype, name)
    except Exception as e:
        return _err(500, str(e))

    if isinstance(doc, dict) and not doc.get("success", True):
        return _err(404, doc.get("error", "Not found"))

    if doc is None:
        return _err(404, "Document not found.")

    return _ok(doc)


async def handle_save_script(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    _, site = load_site_config()
    engine = get_engine(site)

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body."}, status_code=400)

    name = (payload.get("name") or "").strip()
    ref_doctype = (payload.get("ref_doctype") or "").strip()
    doctype_event = (payload.get("doctype_event") or "").strip()
    script_type = payload.get("script_type", "Python")
    script = payload.get("script", "")
    enabled = bool(payload.get("enabled", True))

    if not name:
        return JSONResponse({"error": "Name is required."}, status_code=400)
    if not ref_doctype:
        return JSONResponse({"error": "Reference DocType is required."}, status_code=400)
    if not doctype_event:
        return JSONResponse({"error": "DocType Event is required."}, status_code=400)

    valid_events = {"before_save", "after_save", "before_delete", "after_delete", "on_load"}
    if doctype_event not in valid_events:
        return JSONResponse({"error": f"Invalid event: {doctype_event}"}, status_code=400)

    with engine.begin() as conn:
        existing = conn.execute(
            text('SELECT COUNT(*) FROM "tabServer Script" WHERE name = :name'),
            {"name": name},
        ).scalar()

        if existing:
            conn.execute(
                text("""
                    UPDATE "tabServer Script"
                    SET ref_doctype = :ref_doctype, doctype_event = :doctype_event,
                        script_type = :script_type, script = :script, enabled = :enabled
                    WHERE name = :name
                """),
                {"name": name, "ref_doctype": ref_doctype, "doctype_event": doctype_event,
                 "script_type": script_type, "script": script, "enabled": enabled},
            )
            return JSONResponse({"success": True, "message": "Script updated."})
        else:
            conn.execute(
                text("""
                    INSERT INTO "tabServer Script" (name, ref_doctype, doctype_event, script_type, script, enabled, idx)
                    VALUES (:name, :ref_doctype, :doctype_event, :script_type, :script, :enabled, :idx)
                """),
                {"name": name, "ref_doctype": ref_doctype, "doctype_event": doctype_event,
                 "script_type": script_type, "script": script, "enabled": enabled, "idx": 0},
            )
            return JSONResponse({"success": True, "message": "Script created."}, status_code=201)


async def handle_run_report(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    try:
        result = run_report(name)
    except Exception as e:
        return _err(500, str(e))
    if not result["success"]:
        return _err(404, result["error"])
    return _ok({"name": name, "columns": list(result["data"][0].keys()) if result["data"] else [], "rows": result["data"], "count": result["count"]})


async def handle_resource_update(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    raw_dt = request.path_params.get("doctype", "")
    raw_name = request.path_params.get("name", "")
    doctype = urllib.parse.unquote(raw_dt)
    name = urllib.parse.unquote(raw_name)
    user = _get_user(request)
    ok, msg = authorize(doctype, user, "write")
    if not ok:
        return _err(403, msg)

    try:
        payload = await request.json()
    except Exception:
        return _err(400, "Invalid JSON body.")

    if not isinstance(payload, dict):
        return _err(400, "Request body must be a JSON object.")

    try:
        result = update_document(doctype, name, payload)
    except Exception as e:
        return _err(500, str(e))

    if not result["success"]:
        err_msg = result.get("error", "Error")
        if "not found" in err_msg.lower() or "not applied" in err_msg.lower():
            return _err(404, err_msg)
        return _err(400, err_msg, result.get("errors"))

    return _ok(result["data"])


async def handle_resource_delete(request):
    if require_auth(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    raw_dt = request.path_params.get("doctype", "")
    raw_name = request.path_params.get("name", "")
    doctype = urllib.parse.unquote(raw_dt)
    name = urllib.parse.unquote(raw_name)
    user = _get_user(request)
    ok, msg = authorize(doctype, user, "delete")
    if not ok:
        return _err(403, msg)

    try:
        result = delete_document(doctype, name)
    except Exception as e:
        return _err(500, str(e))

    if not result["success"]:
        err_msg = result.get("error", "Error")
        if "not found" in err_msg.lower() or "not applied" in err_msg.lower():
            return _err(404, err_msg)
        return _err(400, err_msg)

    return _ok(result["data"])
