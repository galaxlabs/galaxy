# Galaxy Project Structure

```
E:\Projects\galaxy\                    # Project root
├── galaxy/                            # Application package
│   ├── __init__.py
│   ├── app.py                         # Starlette ASGI app, routes, middleware
│   │
│   ├── api/                           # REST API layer
│   │   ├── __init__.py
│   │   ├── handlers.py                # 20+ CRUD + auth + report endpoints
│   │   ├── builder.py                 # DocType builder API
│   │   ├── builder_repository.py      # Builder persistence
│   │   ├── bench.py                   # Bench platform API
│   │   └── phase4.py                  # Phase 4 enforcement helpers
│   │
│   ├── auth/                          # Desk auth (sessions, passwords)
│   │   ├── __init__.py
│   │
│   ├── bench_manager/                 # Bench platform management
│   │   ├── platfrom_db.py
│   │   └── site_manager.py
│   │
│   ├── commands/                      # Typer CLI entry points
│   │   ├── __init__.py
│   │   ├── app.py                     # Main CLI (galaxy)
│   │   ├── doctor.py                  # Health check
│   │   ├── install.py                 # Bootstrap installer
│   │   ├── reset.py                   # Drop + recreate tables
│   │   └── start.py                   # HTTP server launcher
│   │
│   ├── config/                        # Site configuration
│   │   ├── __init__.py                # load_site_config(), load_common_config()
│   │
│   ├── database/                      # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py              # SQLAlchemy engine factory
│   │   ├── core_tables.py             # 32 table DDLs (CREATE TABLE IF NOT EXISTS)
│   │   └── seed.py                    # Idempotent data seeding (30 DocTypes)
│   │
│   ├── desk/                          # Desk UI (Jinja2 templates)
│   │   ├── components/
│   │   │   └── ui.py                  # UI component helpers
│   │   └── templates/                 # *.html templates
│   │
│   ├── installer/                     # Bootstrap installation orchestrator
│   │   ├── __init__.py                # run_install(), doctor()
│   │
│   ├── model/                         # Metadata engines (core of Galaxy)
│   │   ├── __init__.py
│   │   ├── document.py                # CRUD engine (create/read/update/delete)
│   │   ├── repository.py              # Metadata queries (get_runtime_meta, etc.)
│   │   ├── runtimemeta.py             # RuntimeMeta dataclass + merge_meta()
│   │   ├── meta_cache.py              # LRU TTL cache for RuntimeMeta
│   │   ├── script_engine.py           # Server script runner
│   │   ├── field_rule_engine.py       # Field validation + _safe_eval()
│   │   ├── field_dependency_engine.py # Show/hide/require logic
│   │   ├── computed_field_engine.py   # Formula evaluation
│   │   ├── display_logic_engine.py    # Visibility resolver
│   │   ├── dynamic_source_engine.py   # Dynamic field options
│   │   ├── permission_engine.py       # Phase 4: field perms, masks, rules
│   │   ├── migration_planner.py       # ALTER TABLE planning
│   │   └── migration_applier.py       # ALTER TABLE execution
│   │
│   ├── portal/                        # Portal subsystem
│   │   ├── __init__.py
│   │   ├── auth.py                    # Signup, login, session
│   │   ├── api.py                     # Page handlers
│   │   ├── permissions.py             # PortalPermissionEngine
│   │   └── resource.py                # Portal CRUD resource handlers
│   │
│   ├── reports/                       # Report engine
│   │   ├── __init__.py
│   │   └── engine.py
│   │
│   ├── security/                      # Security utilities
│   │   ├── __init__.py                # CSRF, rate limiting, SQL injection scan
│   │
│   ├── tenant/                        # Multi-tenant context
│   │   ├── __init__.py                # Tenant context, API handlers
│   │
│   └── permissions/                   # Phase 1 doc-level RBAC
│       ├── __init__.py                # authorize(), get_user_roles()
│
├── tests/                             # 371 pytest tests
│   ├── test_seed.py                   # Core seed validation
│   ├── test_crud.py                   # CRUD operations
│   ├── test_crud_engine_integration.py # CRUD + field rules + computed fields
│   ├── test_auth.py                   # Desk auth + session
│   ├── test_security.py               # CSRF, rate limiting, SQL guard
│   ├── test_tenant.py                 # Tenant CRUD
│   ├── test_tenant_isolation.py       # Tenant isolation
│   ├── test_config.py                 # Config loading
│   ├── test_connection.py             # DB connection
│   ├── test_meta_cache.py             # LRU cache
│   ├── test_runtimemeta.py            # Merge meta
│   ├── test_field_rule_engine.py      # Field rules
│   ├── test_field_dependency_engine.py # Field dependencies
│   ├── test_computed_field_engine.py  # Computed fields
│   ├── test_display_logic_engine.py   # Display logic
│   ├── test_dynamic_source_engine.py  # Dynamic sources
│   ├── test_permission_engine.py      # Phase 4 runtime
│   ├── test_portal_auth.py            # Portal auth
│   ├── test_portal_phase3.py          # Portal CRUD + permissions
│   ├── test_bench.py                  # Bench management
│   ├── test_phase2_seed.py            # Phase 2 seed validation
│   ├── test_phase3_seed.py            # Phase 3 seed validation
│   ├── test_phase3_merge_engine.py    # Phase 3 merge
│   ├── test_phase4_seed.py            # Phase 4 seed validation
│   ├── test_phase4_merge_engine.py    # Phase 4 merge
│   ├── test_phase4_runtime.py         # Phase 4 runtime engines
│   ├── test_phase5_seed.py            # Phase 5 seed validation
│   └── test_phase5_merge_engine.py    # Phase 5 merge
│
├── sites/                             # Site configurations per hostname
│   ├── common_site_config.json        # Global defaults
│   └── default.local/                 # Default site
│       └── site_config.json
│
├── docs/                              # Phase documentation
│
├── tools/                             # Helper scripts
│
├── pyproject.toml                     # Project metadata + dependencies
├── README.md                          # Project introduction
├── STRUCTURE.md                       # This file
└── .gitignore
```
