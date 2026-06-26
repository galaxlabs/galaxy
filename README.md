# Galaxy

**Metadata-driven full-stack low-code application framework.**  
Built with Python, PostgreSQL, Starlette, and SQLAlchemy.

Galaxy is a low-code framework inspired by Frappe/ERPNext that lets you define data models (DocTypes) through a visual builder UI, then automatically generates database tables, REST APIs, and desk interfaces — all without writing boilerplate. Metadata is the source of truth.

## Status

**371 tests, 0 failures.** Core framework phases 1–5 and Portal phase 3 implemented.

| Phase | Layer | Status |
|-------|-------|--------|
| 1 | Bootstrap, Config, Auth, Session, Desk UI, CRUD REST API | Done |
| 2 | Field Rules (validation), Field Dependencies, Computed Fields | Done |
| 3 | FieldRule + FieldDependency + ComputedField engines, CRUD integration | Done |
| 3 Portal | Portal Permission Engine, CRUD API, Profile Links, Field Permissions | Done |
| 4 | Field Permissions, Data Mask Rules, Permission Rules (runtime) | Done |
| 5 | Display Logic, Dynamic Field Sources, merge + engine | Done |
| 6+ | Field Type registry, Document export, advanced dependencies | Planned |

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16 (Docker recommended)

### Setup

```powershell
docker compose up -d
pip install -e .
galaxy install
galaxy doctor
galaxy start
```

### Verify

```powershell
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/api/version
```

### Reset

```powershell
galaxy reset
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `galaxy install` | Bootstrap a Galaxy site |
| `galaxy doctor`  | Check installation health |
| `galaxy start`   | Start the HTTP server |
| `galaxy reset`   | Drop and recreate core tables |

## Architecture

Metadata is the source of truth — no hard-coded tables or controllers for business objects. All data models (DocTypes) are defined as metadata records in core tables (`tabDocType`, `tabDocField`, `tabDocPerm`). Runtime metadata is assembled from layered sources:

1. **Base** — DocType + DocField + DocPerm definitions
2. **Custom** — CustomField + PropertySetter overlays (never modify base JSON)
3. **Settings** — DocType-level configuration
4. **Phase 2–5** — Field Rules, Dependencies, Computed Fields, Field Permissions, Data Masks, Permission Rules, Display Logic, Dynamic Sources

Layers merge via `RuntimeMeta` / `merge_meta()` — a pure function combining all layers into a single object consumed by engines at runtime.

### Directory Structure

```
galaxy/
├── galaxy/                        # Application package
│   ├── app.py                     # ASGI app: routes, middleware, exception handlers
│   ├── api/                       # REST API handlers + Phase 4 integration
│   │   ├── handlers.py            # 20+ resource endpoints
│   │   ├── builder.py             # DocType builder
│   │   ├── bench.py               # Bench platform API
│   │   └── phase4.py              # Phase 4 field permission + data mask helpers
│   ├── commands/                  # CLI entry points (Typer)
│   │   ├── app.py                 # Main CLI
│   │   └── install.py / start.py / reset.py / doctor.py
│   ├── config/                    # Site configuration
│   ├── database/                  # Database connection + DDL
│   │   ├── connection.py          # SQLAlchemy engine (pooled)
│   │   ├── core_tables.py         # 32 table DDLs
│   │   ├── seed.py                # Idempotent data seeding (30 Doctypes)
│   │   └── meta_cache.py
│   ├── desk/                      # Desk UI (Jinja2 templates)
│   ├── installer/                 # Bootstrap installation
│   ├── model/                     # Metadata engines
│   │   ├── document.py            # CRUD engine (create/read/update/delete)
│   │   ├── repository.py          # Metadata repository layer
│   │   ├── runtimemeta.py         # RuntimeMeta + merge_meta()
│   │   ├── field_rule_engine.py   # Field validation
│   │   ├── field_dependency_engine.py  # Show/hide/require logic
│   │   ├── computed_field_engine.py    # Expression evaluation
│   │   ├── display_logic_engine.py     # Visibility resolver
│   │   ├── dynamic_source_engine.py    # Dynamic field options
│   │   ├── permission_engine.py        # Phase 4: field perms + masks + rules
│   │   ├── script_engine.py            # Server scripts
│   │   ├── meta_cache.py               # LRU cache
│   │   └── migration_*.py              # Migration planner + applier
│   ├── portal/                    # Portal auth + CRUD + permission engine
│   │   ├── auth.py                # Portal session + signup
│   │   ├── api.py                 # Portal page handlers
│   │   ├── permissions.py         # PortalPermissionEngine
│   │   └── resource.py            # Portal CRUD resource handlers
│   ├── reports/                   # Report engine
│   ├── security/                  # CSRF, rate limiting, audit
│   ├── tenant/                    # Multi-tenant context
│   └── permissions/               # Phase 1 doc-level RBAC
├── tests/                         # 371 tests (pytest)
├── sites/                         # Site configurations
├── docs/                          # Documentation
├── tools/                         # Helper scripts
└── pyproject.toml                 # Project metadata
```

### Seeded DocTypes

30 DocTypes across all phases: Core (DocType, DocField, DocPerm, User, Role, etc.), Phase 2 (FieldRule, FieldDependency, ComputedField), Phase 3 Portal (PortalUser, PortalRole, PortalPermission, PortalSession, PortalProfileLink, PortalFieldPermission), Phase 4 (FieldPermission, DataMaskRule, PermissionRule), Phase 5 (DisplayLogic, DynamicFieldSource).

## Tests

```powershell
pytest
```

371 tests covering seed validation, merge engine, CRUD operations, field rules, dependencies, computed fields, display logic, dynamic sources, Phase 4 runtime engines, Portal auth + CRUD, security, migration, tenant isolation, and bench management.

## CLI

Galaxy is the installed command — entry point `galaxy.commands.app:main`.
