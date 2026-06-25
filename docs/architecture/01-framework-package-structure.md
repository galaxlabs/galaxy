# Framework Package Structure

## Physical Layout

```
galaxy/                          # Repository root
├── cmd/                         # Entry points
│   ├── galaxy/main.py           # CLI: python -m cmd.galaxy.main → internal.cli.app:main
│   └── server/main.py           # Server: python -m cmd.server.main → internal.http.server:run_server()
├── internal/                    # Engine package (single Python package)
│   ├── __init__.py              # Version = "0.0.1"
│   ├── bench/                   # Multi-site bench manager
│   │   ├── platform_db.py       # SQLite platform DB (site registry)
│   │   └── site_manager.py      # Site CRUD, backup/restore, app management
│   ├── bootstrap/               # Install / doctor / reset orchestration
│   │   └── installer.py         # run_install(), run_doctor(), run_reset()
│   ├── cli/                     # Typer commands
│   │   ├── app.py               # Root CLI: galaxy install|doctor|start|reset|bench|tenant
│   │   ├── bench.py             # galaxy bench (13 sub-commands)
│   │   ├── doctor.py            # galaxy doctor
│   │   ├── install.py           # galaxy install
│   │   ├── reset.py             # galaxy reset
│   │   ├── start.py             # galaxy start
│   │   └── tenant.py            # galaxy tenant (4 sub-commands)
│   ├── config/                  # Configuration loading
│   │   └── site_config.py       # load_common_config(), load_site_config()
│   ├── core/                    # Business logic
│   │   ├── api.py               # All HTTP handler functions
│   │   ├── auth.py              # Password verify, session create/get/delete
│   │   ├── bench_api.py         # HTTP handlers for bench operations
│   │   ├── builder.py           # DocType payload validation + JSON builder
│   │   ├── builder_repository.py# DocType metadata persistence
│   │   ├── crud.py              # Generic document CRUD (create/list/get/update/delete)
│   │   ├── migration_applier.py # CREATE TABLE execution
│   │   ├── migration_planner.py # Migration plan generation
│   │   ├── permissions.py       # Role-based access control
│   │   ├── report_engine.py     # Query + Script report runner
│   │   ├── repository.py        # Read-only metadata queries
│   │   ├── script_engine.py     # Server-side Python script execution
│   │   ├── security.py          # CSRF, rate limit, security events
│   │   └── tenant.py            # Tenant resolution + API handlers
│   ├── db/                      # Database layer
│   │   ├── connection.py        # Engine creation, connection string
│   │   ├── core_tables.py       # CREATE TABLE DDL for 14 core tables
│   │   └── seed.py              # Seed data (doctypes, fields, roles, admin)
│   ├── http/                    # Web server
│   │   ├── server.py            # Starlette app: 46 routes + middleware
│   │   ├── static/desk.css      # Desk UI styles
│   │   └── templates/           # 16 Jinja2 templates
│   └── site/                    # (reserved)
├── sites/                       # Site config files (site_config.json per site)
├── tests/                       # 10 test files, 153 tests
├── docs/                        # Documentation
├── README.md                    # Quick start
├── ROADMAP.md                   # Milestone tracking
├── VISION.md                    # Long-term vision
├── pyproject.toml               # Dependencies, build config, tool config
├── .env.example                 # Environment variables
└── docker-compose.yml           # PostgreSQL 16
```

## Separation Principles

1. **Framework engine** lives entirely inside `internal/`. It is a single deployable package.
2. **Entry points** in `cmd/` are thin wrappers that set `sys.path` and delegate.
3. **Site data** lives in `sites/<name>/site_config.json` — never inside `internal/`.
4. **Apps** (business plugins) will live in `apps/` in a future milestone.
5. **Tests** mirror the internal structure but are flat under `tests/`.

## No Circular Imports Rule

Dependency direction:

```
cmd → internal/cli → internal/{bootstrap,config} → internal/db → internal/core/* → internal/http
```

- `internal/db/` never imports from `internal/core/` or `internal/http/`.
- `internal/core/` never imports from `internal/http/`.
- `internal/http/` imports from `internal/core/` for handlers.
- `internal/core/` modules may import from `internal/db/` and `internal/config/`.
- Tenant module (`internal/core/tenant.py`) uses lazy imports for auth/CSRF to avoid cycles with `internal/core/api.py`.

## Future Target Layout (Frappe-style)

```
galaxy/                       # Framework package
apps/                         # Business apps (plugins)
sites/                        # Site-specific configs
logs/                         # Server logs
config/                       # Common config
```