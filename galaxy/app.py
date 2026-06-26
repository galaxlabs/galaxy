import os
import urllib.parse

import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.types import ASGIApp

from galaxy.config import load_site_config
from galaxy.api.handlers import (
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
    handle_resource_export,
    handle_resource_get,
    handle_resource_list,
    handle_resource_update,
    handle_run_report,
    handle_save_script,
    handle_summary,
    require_auth,
)
from galaxy.api.bench import (
    handle_bench_backup,
    handle_bench_create_site,
    handle_bench_install_app,
    handle_bench_list_backups,
    handle_bench_migration_status,
    handle_bench_restore,
    handle_bench_site_apps,
    handle_bench_site_detail,
    handle_bench_sites,
    handle_bench_uninstall_app,
)
from galaxy.model.document import get_crud_fields, get_doctype_for_crud
from galaxy.model.document import get_document as crud_get_document
from galaxy.model.migration_planner import plan_doctype_migration
from galaxy.model.repository import (
    get_core_summary,
    get_doctype,
    get_doctype_fields,
    get_doctype_permissions,
    get_doctypes,
    get_runtime_meta,
)
from galaxy.tenant import (
    current_tenant,
    get_tenant_id,
    handle_tenant_create,
    handle_tenant_delete,
    handle_tenant_get,
    handle_tenant_list,
    handle_tenant_update,
)
from galaxy.desk.components import ui
from galaxy.portal.api import (
    handle_portal_home,
    handle_portal_login,
    handle_portal_login_page,
    handle_portal_logout,
    handle_portal_me,
    handle_portal_profile,
    handle_portal_signup,
    handle_portal_signup_page,
)
from galaxy.portal.resource import (
    portal_create,
    portal_list,
    portal_get,
    portal_update,
    portal_delete,
)


def _slugify(name):
    import re
    return re.sub(r"[^a-z0-9]", "-", name.lower()).strip("-")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "desk", "templates")
COMPONENTS_DIR = os.path.join(BASE_DIR, "desk", "components")
STATIC_DIR = os.path.join(BASE_DIR, "desk", "static")

templates = Jinja2Templates(directory=[TEMPLATES_DIR, COMPONENTS_DIR])
templates.env.globals["ui"] = ui
templates.env.filters["slugify"] = _slugify


async def homepage(request):
    return JSONResponse({"app": "galaxy", "status": "running"})


async def health(request):
    try:
        from galaxy.database.connection import get_engine, test_connection
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
    return await _desk_render(request, "login.html", {})


async def desk_dashboard(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    summary = get_core_summary()
    return await _desk_render(request, "desk.html", {"summary": summary})


async def desk_doctypes(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    doctypes = get_doctypes()
    return await _desk_render(request, "doctypes.html", {"doctypes": doctypes})


async def desk_builder_new(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    return await _desk_render(request, "doctype_builder_new.html", {})


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


async def desk_ui_guide(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    return await _desk_render(request, "ui_guide.html", {})


async def desk_reports(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    from sqlalchemy import text

    from galaxy.database.connection import get_engine
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT name, ref_doctype, report_type, enabled FROM "tabReport" ORDER BY idx')
        ).mappings().all()
    reports = [dict(r) for r in rows]
    return await _desk_render(request, "reports.html", {"reports": reports})


async def desk_report_detail(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    from sqlalchemy import text

    from galaxy.database.connection import get_engine
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
    return await _desk_render(request, "report_detail.html", {"report": report})


async def desk_scripts(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    from sqlalchemy import text

    from galaxy.database.connection import get_engine
    _, site = load_site_config()
    engine = get_engine(site)
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT name, ref_doctype, doctype_event, enabled FROM "tabServer Script" ORDER BY idx')
        ).mappings().all()
    scripts = [dict(r) for r in rows]
    return await _desk_render(request, "server_scripts.html", {"scripts": scripts})


async def desk_script_new(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    doctypes = get_doctypes()
    events = ["before_save", "after_save", "before_delete", "after_delete", "on_load"]
    return await _desk_render(request, "server_script_form.html", {"title": "New Server Script", "script": None, "doctypes": doctypes, "events": events})


async def desk_script_edit(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw = request.path_params.get("name", "")
    name = urllib.parse.unquote(raw)
    from sqlalchemy import text

    from galaxy.database.connection import get_engine
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
    return await _desk_render(request, "server_script_form.html", {"title": f"Edit: {name}", "script": script, "doctypes": doctypes, "events": events})


async def desk_bench(request):
    from galaxy.bench_manager.platform_db import init_platform_db, list_sites
    init_platform_db()
    sites = list_sites()
    return await _desk_render(request, "bench.html", {"sites": sites})


async def desk_bench_site(request):
    name = request.path_params.get("name", "")
    from galaxy.bench_manager.platform_db import get_site, init_platform_db
    init_platform_db()
    site = get_site(name)
    if site is None:
        return JSONResponse({"error": "Site not found."}, status_code=404)
    return await _desk_render(request, "bench_site.html", {"site": site})


async def desk_bench_new(request):
    return await _desk_render(request, "bench_new.html", {})


async def desk_tenants(request):
    return await _desk_render(request, "tenants.html", {})


def _get_table_columns(doctype_name):
    meta = get_runtime_meta(doctype_name)
    if meta is None:
        return []
    cols = [{"key": f["fieldname"], "label": f.get("label") or f["fieldname"], "type": f["fieldtype"], "sortable": f["fieldtype"] not in ("Text", "Table", "Code")} for f in meta.fields if f["fieldname"] != "name"]
    cols.insert(0, {"key": "name", "label": "Name", "type": "Data", "sortable": True})
    return cols

def _list_records(doctype_name, page=1, limit=20, sort_by="name", sort_order="asc", search=""):
    doctype = get_doctype_for_crud(doctype_name)
    if doctype is None:
        return [], 0, doctype
    meta = get_runtime_meta(doctype_name)
    table_name = doctype["table_name"]
    col_names = ["name"] + [f["fieldname"] for f in (meta.fields if meta else []) if f["fieldname"] != "name"]

    from sqlalchemy import text

    from galaxy.config import load_site_config
    from galaxy.database.connection import get_engine
    from galaxy.database.core_tables import TENANT_TABLES

    _, site = load_site_config()
    engine = get_engine(site)
    tenant_id = current_tenant.get()

    params = {}
    where_parts = []
    if tenant_id and table_name in TENANT_TABLES:
        where_parts.append('tenant_id = :_tenant')
        params['_tenant'] = tenant_id
    if search:
        like = '%' + search + '%'
        search_clauses = [f'"{c}" ILIKE :_s' for c in col_names if c != "name"]
        search_clauses.insert(0, '"name" ILIKE :_s')
        where_parts.append('(' + ' OR '.join(search_clauses) + ')')
        params['_s'] = like

    where = ' AND '.join(where_parts) if where_parts else '1=1'
    quoted_table = '"' + table_name + '"'

    safe_sort = sort_by if sort_by in col_names else "name"
    safe_order = "ASC" if sort_order.lower() != "desc" else "DESC"
    offset = (page - 1) * limit

    count_sql = f'SELECT COUNT(*) FROM {quoted_table} WHERE {where}'
    data_sql = f'SELECT * FROM {quoted_table} WHERE {where} ORDER BY "{safe_sort}" {safe_order} LIMIT :_lim OFFSET :_off'
    params['_lim'] = limit
    params['_off'] = offset

    with engine.connect() as conn:
        total = conn.execute(text(count_sql), params).scalar() or 0
        rows = conn.execute(text(data_sql), params).mappings().all()
    return [dict(r) for r in rows], total, doctype


async def desk_resource_list(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw = request.path_params.get("doctype", "")
    doctype_name = urllib.parse.unquote(raw)

    page = int(request.query_params.get("page", "1"))
    limit = int(request.query_params.get("limit", "20"))
    sort_by = request.query_params.get("sort_by", "name")
    sort_order = request.query_params.get("sort_order", "asc")
    search = request.query_params.get("search", "")

    records, total, doctype = _list_records(doctype_name, page, limit, sort_by, sort_order, search)
    if doctype is None:
        return JSONResponse({"error": "DocType not found"}, status_code=404)

    columns = _get_table_columns(doctype_name)

    if request.headers.get("HX-Request") == "true":
        from galaxy.desk.components.table import datatable
        html = datatable(doctype_name, columns, records, total, page, limit, sort_by, sort_order, search)
        return HTMLResponse(html)

    return await _desk_render(request, "desk_list.html", {
        "doctype": doctype_name,
        "columns": columns,
        "records": records,
        "total": total,
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "search": search,
    })


async def desk_resource_new(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw = request.path_params.get("doctype", "")
    doctype_name = urllib.parse.unquote(raw)

    meta = get_runtime_meta(doctype_name)
    if meta is None:
        return JSONResponse({"error": "DocType not found"}, status_code=404)

    return await _desk_render(request, "desk_form.html", {
        "doctype": doctype_name, "title": f"New {doctype_name}",
        "fields": meta.fields, "record": None,
        "meta": meta,
    })


async def desk_resource_detail(request):
    if require_auth(request) is None:
        return RedirectResponse(url="/login", status_code=302)
    raw_dt = request.path_params.get("doctype", "")
    raw_name = request.path_params.get("name", "")
    doctype_name = urllib.parse.unquote(raw_dt)
    name = urllib.parse.unquote(raw_name)

    meta = get_runtime_meta(doctype_name)
    if meta is None:
        return JSONResponse({"error": "DocType not found"}, status_code=404)

    doc = crud_get_document(doctype_name, name)
    if doc is None:
        return JSONResponse({"error": "Record not found"}, status_code=404)

    return await _desk_render(request, "desk_form.html", {
        "doctype": doctype_name, "title": f"{name}",
        "fields": meta.fields, "record": doc,
        "meta": meta,
    })


# ── Route Protection ──────────────────────────────────────────────


def _path_matches(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


PROTECTED_DESK_PREFIXES = ["/desk"]
PROTECTED_API_PREFIXES = [
    "/api/resource",
    "/api/core/scripts",
    "/api/report",
    "/api/reports",
    "/api/server-script",
    "/api/scripts",
    "/api/builder",
    "/api/auth/me",
    "/api/bench",
]
PUBLIC_EXACT = {
    "/",
    "/health",
    "/api",
    "/api/version",
    "/login",
    "/api/auth/login",
    "/api/auth/logout",
    "/api/portal/auth/login",
    "/api/portal/auth/signup",
    "/api/portal/auth/logout",
}
PUBLIC_PREFIXES = ["/static", "/assets", "/favicon.ico", "/desk/assets"]
PORTAL_PROTECTED_PREFIXES = ["/api/portal/auth/me", "/api/portal/auth/logout", "/api/portal/profile", "/api/portal/resource"]
PORTAL_PAGE_PREFIXES = ["/portal"]

ALLOWED_CORE_PREFIXES = [
    "/api/core/installed-apps",
    "/api/core/installed-modules",
    "/api/core/modules",
    "/api/core/doctypes",
    "/api/core/summary",
]


def _is_protected(path: str) -> tuple[bool, bool]:
    for p in PUBLIC_EXACT:
        if path == p:
            return False, False
    for p in PUBLIC_PREFIXES:
        if _path_matches(path, p):
            return False, False
    for p in ALLOWED_CORE_PREFIXES:
        if _path_matches(path, p):
            return False, False

    for p in PROTECTED_DESK_PREFIXES:
        if _path_matches(path, p):
            return True, False

    for p in PROTECTED_API_PREFIXES:
        if _path_matches(path, p):
            return True, True

    for p in PORTAL_PROTECTED_PREFIXES:
        if _path_matches(path, p):
            return True, True

    if path.startswith("/api/migration/") and path.endswith("/apply"):
        return True, True

    return False, False


class RequireSessionMiddleware:
    def __init__(self, app):
        self.app = app
        self._portal_prefixes = ["/api/portal", "/portal"]

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        protected, is_api = _is_protected(path)
        is_portal = any(path.startswith(p) for p in self._portal_prefixes)

        if not protected:
            await self.app(scope, receive, send)
            return

        from starlette.requests import Request
        request = Request(scope, receive)

        if is_portal:
            from galaxy.portal.auth import portal_require_session
            session = portal_require_session(request)
            if session is not None:
                request.state.portal_session = session
                await self.app(scope, receive, send)
                return
            if is_api:
                response = JSONResponse({"success": False, "error": "Portal authentication required."}, status_code=401)
                await response(scope, receive, send)
            else:
                response = RedirectResponse(url="/portal/login", status_code=302)
                await response(scope, receive, send)
            return

        tenant_id = get_tenant_id(request)
        from galaxy.tenant import current_tenant
        current_tenant.set(tenant_id)
        request.state.tenant_id = tenant_id

        from galaxy.auth import require_session
        user = require_session(request)
        if user is not None:
            request.state.user = user
            await self.app(scope, receive, send)
            return

        if is_api:
            response = JSONResponse(
                {"success": False, "error": "Authentication required."},
                status_code=401,
            )
            await response(scope, receive, send)
        else:
            response = RedirectResponse(url="/login", status_code=302)
            await response(scope, receive, send)


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
    Route("/api/resource/{doctype}/export", endpoint=handle_resource_export),
    Route("/api/resource/{doctype}/{name}", endpoint=handle_resource_get),
    Route("/api/resource/{doctype}/{name}", endpoint=handle_resource_update, methods=["PUT"]),
    Route("/api/resource/{doctype}/{name}", endpoint=handle_resource_delete, methods=["DELETE"]),
    Route("/api/core/scripts", endpoint=handle_save_script, methods=["POST"]),
    Route("/api/report/{name}", endpoint=handle_run_report),
    Route("/api/bench/sites", endpoint=handle_bench_sites),
    Route("/api/bench/sites", endpoint=handle_bench_create_site, methods=["POST"]),
    Route("/api/bench/sites/{name}", endpoint=handle_bench_site_detail),
    Route("/api/bench/sites/{name}/apps", endpoint=handle_bench_site_apps),
    Route("/api/bench/sites/{name}/apps", endpoint=handle_bench_install_app, methods=["POST"]),
    Route("/api/bench/sites/{name}/apps", endpoint=handle_bench_uninstall_app, methods=["DELETE"]),
    Route("/api/bench/sites/{name}/backup", endpoint=handle_bench_backup, methods=["POST"]),
    Route("/api/bench/sites/{name}/backups", endpoint=handle_bench_list_backups),
    Route("/api/bench/sites/{name}/restore", endpoint=handle_bench_restore, methods=["POST"]),
    Route("/api/bench/sites/{name}/migrations", endpoint=handle_bench_migration_status),
    Route("/api/tenants", endpoint=handle_tenant_list),
    Route("/api/tenants", endpoint=handle_tenant_create, methods=["POST"]),
    Route("/api/tenants/{name}", endpoint=handle_tenant_get),
    Route("/api/tenants/{name}", endpoint=handle_tenant_update, methods=["PUT"]),
    Route("/api/tenants/{name}", endpoint=handle_tenant_delete, methods=["DELETE"]),
    Route("/desk", endpoint=desk_dashboard),
    Route("/desk/builder/doctype/new", endpoint=desk_builder_new),
    Route("/desk/ui-guide", endpoint=desk_ui_guide),
    Route("/desk/doctypes", endpoint=desk_doctypes),
    Route("/desk/doctypes/{name}", endpoint=desk_doctype_detail),
    Route("/desk/reports", endpoint=desk_reports),
    Route("/desk/reports/{name}", endpoint=desk_report_detail),
    Route("/desk/scripts", endpoint=desk_scripts),
    Route("/desk/scripts/new", endpoint=desk_script_new),
    Route("/desk/scripts/{name}", endpoint=desk_script_edit),
    Route("/desk/resource/{doctype}", endpoint=desk_resource_list),
    Route("/desk/resource/{doctype}/list", endpoint=desk_resource_list),
    Route("/desk/resource/{doctype}/new", endpoint=desk_resource_new),
    Route("/desk/resource/{doctype}/{name}", endpoint=desk_resource_detail),
    Route("/desk/bench", endpoint=desk_bench),
    Route("/desk/bench/sites/new", endpoint=desk_bench_new),
    Route("/desk/bench/sites/{name}", endpoint=desk_bench_site),
    Route("/desk/tenants", endpoint=desk_tenants),
    Route("/portal", endpoint=handle_portal_home),
    Route("/portal/login", endpoint=handle_portal_login_page),
    Route("/portal/signup", endpoint=handle_portal_signup_page),
    Route("/api/portal/auth/login", endpoint=handle_portal_login, methods=["POST"]),
    Route("/api/portal/auth/signup", endpoint=handle_portal_signup, methods=["POST"]),
    Route("/api/portal/auth/logout", endpoint=handle_portal_logout, methods=["POST"]),
    Route("/api/portal/auth/me", endpoint=handle_portal_me),
    Route("/api/portal/profile", endpoint=handle_portal_profile),
    Route("/api/portal/resource/{doctype}", endpoint=portal_list),
    Route("/api/portal/resource/{doctype}", endpoint=portal_create, methods=["POST"]),
    Route("/api/portal/resource/{doctype}/{docname}", endpoint=portal_get),
    Route("/api/portal/resource/{doctype}/{docname}", endpoint=portal_update, methods=["PUT"]),
    Route("/api/portal/resource/{doctype}/{docname}", endpoint=portal_delete, methods=["DELETE"]),
    Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
]

async def _desk_render(request, template_name: str, context: dict, status_code: int = 200):
    try:
        return templates.TemplateResponse(request, template_name, context, status_code=status_code)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Template render error [{template_name}]: {e}\n{tb}")
        return HTMLResponse(
            f"""<!DOCTYPE html>
<html><head><title>Galaxy — Error</title>
<link rel="stylesheet" href="/static/desk.css">
</head><body style="padding:40px;font-family:system-ui;">
<h1>Internal Server Error</h1>
<pre style="background:#f8d7da;padding:16px;border-radius:8px;white-space:pre-wrap;word-break:break-all;">{e}</pre>
<p><a href="/desk">← Back to Desk</a></p>
</body></html>""",
            status_code=500,
        )


async def server_error_handler(request, exc):
    import traceback
    tb = traceback.format_exc()
    print(f"Unhandled 500 [{request.method} {request.url.path}]: {exc}\n{tb}")
    return HTMLResponse(
        f"""<!DOCTYPE html>
<html><head><title>Galaxy — Error</title>
<link rel="stylesheet" href="/static/desk.css">
</head><body style="padding:40px;font-family:system-ui;">
<h1>Internal Server Error</h1>
<pre style="background:#f8d7da;padding:16px;border-radius:8px;white-space:pre-wrap;word-break:break-all;">{exc}</pre>
<p><a href="/desk">← Back to Desk</a></p>
</body></html>""",
        status_code=500,
    )


starlette_app = Starlette(routes=routes, exception_handlers={500: server_error_handler})

app: ASGIApp = RequireSessionMiddleware(starlette_app)


def run_server(host="127.0.0.1", port=8080):
    uvicorn.run(app, host=host, port=port)
