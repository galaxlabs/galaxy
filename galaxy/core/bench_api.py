from starlette.responses import JSONResponse

from internal.bench.platform_db import get_site, init_platform_db, list_sites, site_exists
from internal.bench.site_manager import (
    backup_site as _backup_site,
)
from internal.bench.site_manager import (
    create_site as _create_site,
)
from internal.bench.site_manager import (
    get_site_migration_status as _get_site_migration_status,
)
from internal.bench.site_manager import (
    install_app as _install_app,
)
from internal.bench.site_manager import (
    list_apps as _list_apps,
)
from internal.bench.site_manager import (
    list_backups as _list_backups,
)
from internal.bench.site_manager import (
    restore_site as _restore_site,
)
from internal.bench.site_manager import (
    uninstall_app as _uninstall_app,
)


async def handle_bench_sites(request):
    init_platform_db()
    sites = list_sites()
    return JSONResponse({"success": True, "data": sites})


async def handle_bench_create_site(request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid JSON body."}, status_code=400)

    name = (payload.get("name") or "").strip()
    if not name:
        return JSONResponse({"success": False, "error": "Site name is required."}, status_code=400)

    db_host = payload.get("db_host", "127.0.0.1")
    db_port = payload.get("db_port", 5432)

    try:
        config = _create_site(name, db_host, db_port)
        return JSONResponse({
            "success": True,
            "data": {
                "name": name,
                "db_name": config["db_name"],
                "db_user": config["db_user"],
            },
        }, status_code=201)
    except ValueError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=409)


async def handle_bench_site_detail(request):
    name = request.path_params.get("name", "")
    init_platform_db()
    site = get_site(name)
    if site is None:
        return JSONResponse({"success": False, "error": "Site not found."}, status_code=404)
    return JSONResponse({"success": True, "data": site})


async def handle_bench_site_apps(request):
    name = request.path_params.get("name", "")
    if not site_exists(name):
        return JSONResponse({"success": False, "error": "Site not found."}, status_code=404)
    try:
        apps = _list_apps(name)
        return JSONResponse({"success": True, "data": apps})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


async def handle_bench_install_app(request):
    name = request.path_params.get("name", "")
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid JSON body."}, status_code=400)

    app_name = (payload.get("app_name") or "").strip()
    if not app_name:
        return JSONResponse({"success": False, "error": "App name is required."}, status_code=400)

    if not site_exists(name):
        return JSONResponse({"success": False, "error": "Site not found."}, status_code=404)

    try:
        config = _install_app(name, app_name)
        return JSONResponse({"success": True, "data": {"installed_apps": config["installed_apps"]}}, status_code=201)
    except ValueError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=409)


async def handle_bench_uninstall_app(request):
    name = request.path_params.get("name", "")
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid JSON body."}, status_code=400)

    app_name = (payload.get("app_name") or "").strip()
    if not app_name:
        return JSONResponse({"success": False, "error": "App name is required."}, status_code=400)

    if not site_exists(name):
        return JSONResponse({"success": False, "error": "Site not found."}, status_code=404)

    try:
        config = _uninstall_app(name, app_name)
        return JSONResponse({"success": True, "data": {"installed_apps": config["installed_apps"]}})
    except ValueError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=404)


async def handle_bench_backup(request):
    name = request.path_params.get("name", "")
    if not site_exists(name):
        return JSONResponse({"success": False, "error": "Site not found."}, status_code=404)

    try:
        result = _backup_site(name)
        return JSONResponse({"success": True, "data": result})
    except (ValueError, RuntimeError) as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


async def handle_bench_list_backups(request):
    name = request.path_params.get("name", "")
    if not site_exists(name):
        return JSONResponse({"success": False, "error": "Site not found."}, status_code=404)

    try:
        backups = _list_backups(name)
        return JSONResponse({"success": True, "data": backups})
    except ValueError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


async def handle_bench_restore(request):
    name = request.path_params.get("name", "")
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid JSON body."}, status_code=400)

    backup_path = (payload.get("backup_path") or "").strip()
    if not backup_path:
        return JSONResponse({"success": False, "error": "Backup path is required."}, status_code=400)

    if not site_exists(name):
        return JSONResponse({"success": False, "error": "Site not found."}, status_code=404)

    try:
        _restore_site(name, backup_path)
        return JSONResponse({"success": True, "data": {"restored": backup_path}})
    except (ValueError, RuntimeError) as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


async def handle_bench_migration_status(request):
    name = request.path_params.get("name", "")
    if not site_exists(name):
        return JSONResponse({"success": False, "error": "Site not found."}, status_code=404)

    try:
        results = _get_site_migration_status(name)
        applied = sum(1 for r in results if r["migration_status"] == "applied")
        pending = sum(1 for r in results if r["migration_status"] == "pending")
        return JSONResponse({
            "success": True,
            "data": {
                "doctypes": results,
                "summary": {"total": len(results), "applied": applied, "pending": pending},
            },
        })
    except ValueError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)
