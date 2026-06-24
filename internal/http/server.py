import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from internal.config.site_config import load_site_config


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


routes = [
    Route("/", endpoint=homepage),
    Route("/health", endpoint=health),
    Route("/api", endpoint=api_root),
    Route("/api/version", endpoint=api_version),
]

app = Starlette(routes=routes)


def run_server(host="127.0.0.1", port=8080):
    uvicorn.run(app, host=host, port=port)
