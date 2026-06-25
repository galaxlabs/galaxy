import os
import urllib.parse

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from internal.config.site_config import load_site_config
from internal.core.api import (
    handle_auth_me,
    handle_builder_preview,
    handle_builder_save,
    handle_doctype,
    handle_doctype_fields,
    handle_doctype_permissions,
    handle_doctypes,
    handle_installed_apps,
    handle_installed_modules,
    handle_login,
    handle_logout,
    handle_migration_apply,
    handle_migration_preview,
    handle_modules,
    handle_resource_create,
    handle_resource_delete,
    handle_resource_get,
    handle_resource_list,
    handle_resource_update,
    handle_run_report,
    handle_save_script,
    handle_summary,
    require_auth,
)
from internal.core.crud import list_documents
from internal.core.migration_planner import plan_doctype_migration
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
    return JSONResponse({"app": "galaxy", "status": "running"})


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
        "app": "galaxy",
        "database": "ok" if db_ok else "error",
        "site": "default.local",
    })


async def api_root(request):
    return JSONResponse({
        "name": "galaxy",
        "engine": "Galaxy Engine",
        "company": "Galaxy Labs",
        "version": "0.0.1",
        "stage": "bootstrap-core",
    })


async def api_version(request):
    return JSONResponse({
        "name": "galaxy",
        "engine": "Galaxy Engine",
        "company": "Galaxy Labs",
        "version": "0.0.1",
        "stage": "bootstrap-core",
    })


async def login_page(request):
    return templates.TemplateResponse(request, "login.html", {})


async def desk_dashboard(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    summary = get_core_summary()
    return templates.TemplateResponse(request, "desk.html", {"summary": summary})


async def desk_doctypes(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    doctypes = get_doctypes()
    return templates.TemplateResponse(request, "doctypes.html", {"doctypes": doctypes})


async def desk_builder_new(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "doctype_builder_new.html", {})


async def desk_doctype_detail(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    doctype = get_doctype(name)
    if doctype is None:
        return JSONResponse({"error": "DocType not found"}, status_code=404)
    fields = get_doctype_fields(name)
    permissions = get_doctype_permissions(name)
    migration_preview = plan_doctype_migration(name)
    return templates.TemplateResponse(
        request,
        "doctype_detail.html",
        {"doctype": doctype, "fields": fields, "permissions": permissions, "migration_preview": migration_preview},
    )


async def desk_resource_list(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw = request.path_params.get("doctype", "")
    doctype_name = urllib.parse.unquote(raw)
    doctype = get_doctype(doctype_name)
    if doctype is None:
        return JSONResponse({"error": "DocType not found"}, status_code=404)
    if doctype.get("migration_status") != "applied":
        return templates.TemplateResponse(
            request,
            "resource_list.html",
            {"doctype": doctype, "columns": [], "records": [], "limit": 0, "total": 0},
        )

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

    all_fields = get_doctype_fields(doctype_name)
    columns = [
        {"fieldname": f["fieldname"], "label": f["label"] or f["fieldname"]}
        for f in all_fields
        if f.get("in_list_view") and not f.get("hidden") and f["fieldtype"] != "Table"
    ]
    columns.insert(0, {"fieldname": "name", "label": "Name"})

    records = list_documents(doctype_name, limit=limit, offset=offset)
    if isinstance(records, dict):
        records = []

    return templates.TemplateResponse(
        request,
        "resource_list.html",
        {"doctype": doctype, "columns": columns, "records": records, "limit": limit, "total": len(records)},
    )


async def desk_reports(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    from sqlalchemy import text

    from internal.db.connection import get_engine
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT name, ref_doctype, report_type, enabled FROM "tabReport" ORDER BY idx')
        ).mappings().all()
    reports = [dict(r) for r in rows]
    return templates.TemplateResponse(request, "reports.html", {"reports": reports})


async def desk_report_detail(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    from sqlalchemy import text

    from internal.db.connection import get_engine
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.connect() as conn:
        row = conn.execute(
            text('SELECT name, ref_doctype, report_type, query, script, enabled FROM "tabReport" WHERE name = :name'),
            {"name": name},
        ).mappings().one_or_none()
    if row is None:
        return JSONResponse({"error": "Report not found"}, status_code=404)
    report = dict(row)
    return templates.TemplateResponse(request, "report_detail.html", {"report": report})


async def desk_scripts(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    from sqlalchemy import text

    from internal.db.connection import get_engine
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT name, ref_doctype, doctype_event, enabled FROM "tabServer Script" ORDER BY idx')
        ).mappings().all()
    scripts = [dict(r) for r in rows]
    return templates.TemplateResponse(request, "server_scripts.html", {"scripts": scripts})


async def desk_script_new(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    doctypes = get_doctypes()
    events = ["before_save", "after_save", "before_delete", "after_delete", "on_load"]
    return templates.TemplateResponse(request, "server_script_form.html", {"title": "New Server Script", "script": None, "doctypes": doctypes, "events": events})


async def desk_script_edit(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    from sqlalchemy import text

    from internal.db.connection import get_engine
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.connect() as conn:
        row = conn.execute(
            text('SELECT name, ref_doctype, doctype_event, script_type, script, enabled FROM "tabServer Script" WHERE name = :name'),
            {"name": name},
        ).mappings().one_or_none()
    if row is None:
        return JSONResponse({"error": "Script not found"}, status_code=404)
    script = dict(row)
    doctypes = get_doctypes()
    events = ["before_save", "after_save", "before_delete", "after_delete", "on_load"]
    return templates.TemplateResponse(request, "server_script_form.html", {"title": f"Edit: {name}", "script": script, "doctypes": doctypes, "events": events})


async def desk_resource_detail(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw_dt = request.path_params.get("doctype", "")
    raw_name = request.path_params.get("name", "")
    doctype_name = urllib.parse.unquote(raw_dt)
    name = urllib.parse.unquote(raw_name)

    doctype = get_doctype(doctype_name)
    if doctype is None:
        return JSONResponse({"error": "DocType not found"}, status_code=404)

    from internal.core.crud import get_document as crud_get_document

    doc = crud_get_document(doctype_name, name)
    if doc is None:
        return JSONResponse({"error": "Record not found"}, status_code=404)

    all_fields = get_doctype_fields(doctype_name)
    columns = [
        {"fieldname": f["fieldname"], "label": f["label"] or f["fieldname"]}
        for f in all_fields
        if f["fieldtype"] != "Table"
    ]
    columns.insert(0, {"fieldname": "name", "label": "Name"})

    return templates.TemplateResponse(
        request,
        "resource_detail.html",
        {"doctype": doctype, "record": doc, "columns": columns},
    )


routes = [
    Route("/", endpoint=homepage),
    Route("/health", endpoint=health),
    Route("/login", endpoint=login_page),
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
    Route("/api/auth/login", endpoint=handle_login, methods=["POST"]),
    Route("/api/auth/logout", endpoint=handle_logout, methods=["POST"]),
    Route("/api/auth/me", endpoint=handle_auth_me),
    Route("/api/builder/doctype/preview", endpoint=handle_builder_preview, methods=["POST"]),
    Route("/api/builder/doctype/save", endpoint=handle_builder_save, methods=["POST"]),
    Route("/api/migration/doctype/{name}/preview", endpoint=handle_migration_preview),
    Route("/api/migration/doctype/{name}/apply", endpoint=handle_migration_apply, methods=["POST"]),
    Route("/api/resource/{doctype}", endpoint=handle_resource_list),
    Route("/api/resource/{doctype}", endpoint=handle_resource_create, methods=["POST"]),
    Route("/api/resource/{doctype}/{name}", endpoint=handle_resource_get),
    Route("/api/resource/{doctype}/{name}", endpoint=handle_resource_update, methods=["PUT"]),
    Route("/api/resource/{doctype}/{name}", endpoint=handle_resource_delete, methods=["DELETE"]),
    Route("/api/core/scripts", endpoint=handle_save_script, methods=["POST"]),
    Route("/api/report/{name}", endpoint=handle_run_report),
    Route("/desk", endpoint=desk_dashboard),
    Route("/desk/builder/doctype/new", endpoint=desk_builder_new),
    Route("/desk/doctypes", endpoint=desk_doctypes),
    Route("/desk/doctypes/{name}", endpoint=desk_doctype_detail),
    Route("/desk/reports", endpoint=desk_reports),
    Route("/desk/reports/{name}", endpoint=desk_report_detail),
    Route("/desk/scripts", endpoint=desk_scripts),
    Route("/desk/scripts/new", endpoint=desk_script_new),
    Route("/desk/scripts/{name}", endpoint=desk_script_edit),
    Route("/desk/resource/{doctype}", endpoint=desk_resource_list),
    Route("/desk/resource/{doctype}/{name}", endpoint=desk_resource_detail),
    Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
]

app = Starlette(routes=routes)


def run_server(host="127.0.0.1", port=8080):
    uvicorn.run(app, host=host, port=port)
