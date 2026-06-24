from starlette.responses import JSONResponse

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
