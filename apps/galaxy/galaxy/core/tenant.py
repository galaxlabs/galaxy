import contextvars

from sqlalchemy import text
from starlette.responses import JSONResponse

from galaxy.db.connection import get_engine

current_tenant: contextvars.ContextVar[str] = contextvars.ContextVar("current_tenant", default="Default")


def _get_engine():
    from internal.config.site_config import load_site_config
    _, site = load_site_config()
    return get_engine(site)


def get_tenant_id(request) -> str:
    tenant = request.headers.get("X-Tenant-ID", "").strip()
    if tenant:
        return tenant
    host = request.headers.get("Host", "")
    parts = host.split(".")
    if len(parts) >= 3:
        return parts[0]
    return "Default"


def resolve_tenant(name_or_domain: str) -> dict | None:
    engine = _get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT name, display_name, domain, status FROM \"tabTenant\" WHERE name = :name OR domain = :domain"),
            {"name": name_or_domain, "domain": name_or_domain},
        ).mappings().one_or_none()
    return dict(row) if row else None


def get_tenants() -> list[dict]:
    engine = _get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT name, display_name, domain, status, created_at FROM "tabTenant" ORDER BY name')
        ).mappings().all()
    return [dict(r) for r in rows]


def create_tenant(name: str, display_name: str = "", domain: str = "") -> dict:
    engine = _get_engine()
    from datetime import UTC, datetime
    now = datetime.now(UTC).isoformat()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO "tabTenant" (name, display_name, domain, status, created_at)
                VALUES (:name, :display_name, :domain, 'active', :created_at)
            """),
            {"name": name, "display_name": display_name or name, "domain": domain, "created_at": now},
        )
    return {"name": name, "display_name": display_name or name, "domain": domain, "status": "active"}


def update_tenant(name: str, display_name: str | None = None, domain: str | None = None, status: str | None = None) -> dict | None:
    engine = _get_engine()
    updates = {}
    if display_name is not None:
        updates["display_name"] = display_name
    if domain is not None:
        updates["domain"] = domain
    if status is not None:
        updates["status"] = status
    if not updates:
        return resolve_tenant(name)
    sets = ", ".join(f"{k} = :{k}" for k in updates)
    updates["name"] = name
    with engine.begin() as conn:
        conn.execute(
            text(f"UPDATE \"tabTenant\" SET {sets} WHERE name = :name"),
            updates,
        )
    return resolve_tenant(name)


def delete_tenant(name: str) -> bool:
    engine = _get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text('DELETE FROM "tabTenant" WHERE name = :name'),
            {"name": name},
        )
    return result.rowcount > 0


# ----- API Handlers -----

AUTH_REQUIRED = {"success": False, "error": "Authentication required."}


def _require_session(request):
    from apps.galaxy.galaxy.core.api import require_auth
    return require_auth(request)


def _require_csrf(request):
    from apps.galaxy.galaxy.core.api import _require_csrf
    return _require_csrf(request)


async def handle_tenant_list(request):
    if _require_session(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    try:
        tenants = get_tenants()
        return JSONResponse({"success": True, "data": tenants})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


async def handle_tenant_get(request):
    if _require_session(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    name = request.path_params.get("name", "")
    tenant = resolve_tenant(name)
    if tenant is None:
        return JSONResponse({"success": False, "error": "Tenant not found"}, status_code=404)
    return JSONResponse({"success": True, "data": tenant})


async def handle_tenant_create(request):
    if _require_session(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    if not _require_csrf(request):
        return JSONResponse({"success": False, "error": "Invalid CSRF token."}, status_code=403)
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid JSON body"}, status_code=400)

    name = payload.get("name", "").strip()
    if not name:
        return JSONResponse({"success": False, "error": "Tenant name is required"}, status_code=400)

    existing = resolve_tenant(name)
    if existing:
        return JSONResponse({"success": False, "error": f"Tenant '{name}' already exists"}, status_code=409)

    tenant = create_tenant(name, payload.get("display_name", ""), payload.get("domain", ""))
    return JSONResponse({"success": True, "data": tenant}, status_code=201)


async def handle_tenant_update(request):
    if _require_session(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    if not _require_csrf(request):
        return JSONResponse({"success": False, "error": "Invalid CSRF token."}, status_code=403)
    name = request.path_params.get("name", "")
    existing = resolve_tenant(name)
    if existing is None:
        return JSONResponse({"success": False, "error": "Tenant not found"}, status_code=404)

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid JSON body"}, status_code=400)

    tenant = update_tenant(name, payload.get("display_name"), payload.get("domain"), payload.get("status"))
    return JSONResponse({"success": True, "data": tenant})


async def handle_tenant_delete(request):
    if _require_session(request) is None:
        return JSONResponse(AUTH_REQUIRED, status_code=401)
    if not _require_csrf(request):
        return JSONResponse({"success": False, "error": "Invalid CSRF token."}, status_code=403)
    name = request.path_params.get("name", "")
    deleted = delete_tenant(name)
    if not deleted:
        return JSONResponse({"success": False, "error": "Tenant not found"}, status_code=404)
    return JSONResponse({"success": True, "data": {"deleted": name}})


def get_tenant_engine(tenant_id: str | None = None):
    from internal.config.site_config import load_site_config
    _, site = load_site_config()
    return get_engine(site)
