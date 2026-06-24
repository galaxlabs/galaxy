import urllib.parse

from starlette.responses import JSONResponse

from internal.core.builder import build_doctype_json, validate_doctype_payload
from internal.core.builder_repository import save_doctype_metadata
from internal.core.migration_applier import apply_doctype_migration
from internal.core.migration_planner import plan_doctype_migration
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
