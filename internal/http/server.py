import os
import urllib.parse

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from internal.config.site_config import load_site_config
from internal.core.api import (
    handle_doctype,
    handle_doctype_fields,
    handle_doctype_permissions,
    handle_doctypes,
    handle_installed_apps,
    handle_installed_modules,
    handle_modules,
    handle_summary,
)
from internal.core.repository import (
    get_core_summary,
    get_doctype,
    get_doctype_fields,
    get_doctype_permissions,
    get_doctypes,
)

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


async def homepage(request):
    return JSONResponse({"app": "galaxy-framework", "status": "running"})


async def health(request):
    try:
        from internal.db.connection import get_engine, test_connection
        _, site = load_site_config()
        engine = get_engine(site)
        db_ok = test_connection(engine)
    except Exception:
        db_ok = False

    return JSONResponse({
        "status": "ok" if db_ok else "degraded",
        "app": "galaxy-framework",
        "database": "ok" if db_ok else "error",
        "site": "default.local",
    })


async def api_root(request):
    return JSONResponse({
        "name": "galaxy-framework",
        "engine": "Galaxy Engine",
        "company": "Galaxy Labs",
        "version": "0.0.1",
        "stage": "bootstrap-core",
    })


async def api_version(request):
    return JSONResponse({
        "name": "galaxy-framework",
        "engine": "Galaxy Engine",
        "company": "Galaxy Labs",
        "version": "0.0.1",
        "stage": "bootstrap-core",
    })


async def desk_dashboard(request):
    summary = get_core_summary()
    return templates.TemplateResponse(request, "desk.html", {"summary": summary})


async def desk_doctypes(request):
    doctypes = get_doctypes()
    return templates.TemplateResponse(request, "doctypes.html", {"doctypes": doctypes})


async def desk_doctype_detail(request):
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    doctype = get_doctype(name)
    if doctype is None:
        return JSONResponse({"error": "DocType not found"}, status_code=404)
    fields = get_doctype_fields(name)
    permissions = get_doctype_permissions(name)
    return templates.TemplateResponse(
        request,
        "doctype_detail.html",
        {"doctype": doctype, "fields": fields, "permissions": permissions},
    )


routes = [
    Route("/", endpoint=homepage),
    Route("/health", endpoint=health),
    Route("/api", endpoint=api_root),
    Route("/api/version", endpoint=api_version),
    Route("/api/core/installed-apps", endpoint=handle_installed_apps),
    Route("/api/core/installed-modules", endpoint=handle_installed_modules),
    Route("/api/core/modules", endpoint=handle_modules),
    Route("/api/core/doctypes", endpoint=handle_doctypes),
    Route("/api/core/doctypes/{name}", endpoint=handle_doctype),
    Route("/api/core/doctypes/{name}/fields", endpoint=handle_doctype_fields),
    Route("/api/core/doctypes/{name}/permissions", endpoint=handle_doctype_permissions),
    Route("/api/core/summary", endpoint=handle_summary),
    Route("/desk", endpoint=desk_dashboard),
    Route("/desk/doctypes", endpoint=desk_doctypes),
    Route("/desk/doctypes/{name}", endpoint=desk_doctype_detail),
    Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
]

app = Starlette(routes=routes)


def run_server(host="127.0.0.1", port=8080):
    uvicorn.run(app, host=host, port=port)
