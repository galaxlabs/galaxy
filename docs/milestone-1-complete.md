# Milestone 1 — Galaxy Bootstrap Core

**Status:** Complete
**Date:** 2026-06-25
**Framework:** Galaxy v0.0.1
**Engine:** Galaxy Engine

---

## What Was Built

The bootstrap foundation of Galaxy: a working CLI, database layer, metadata schema, seed data, health checker, and HTTP server.

### CLI Commands

| Command | File | Purpose |
|---------|------|---------|
| `galaxy install` | `internal/cli/install.py` | Bootstrap a site: create config, connect DB, create tables, seed data |
| `galaxy doctor` | `internal/cli/doctor.py` | Verify installation health against all acceptance criteria |
| `galaxy start` | `internal/cli/start.py` | Launch the Galaxy Engine HTTP server |
| `galaxy reset` | `internal/cli/reset.py` | Drop all core tables for a clean reinstall |

### Core Tables (10)

Created in the `tab*` naming convention:

| Table | Purpose |
|-------|---------|
| `tabInstalled App` | Installed apps for this site |
| `tabInstalled Module` | Installed/enabled modules |
| `tabModule Def` | Module definitions |
| `tabDocType` | DocType metadata |
| `tabDocField` | Field definitions per DocType |
| `tabDocPerm` | Permission rules per DocType + Role |
| `tabUser` | User accounts |
| `tabRole` | Role definitions |
| `tabHas Role` | User-role assignments |
| `tabError Log` | Error logging |

### Seed Data

- 1 installed app: `core` v0.0.1
- 6 modules: Core, Setup, Security, Desk, Workspace, Navigation
- 1 Administrator user (bcrypt-hashed password)
- 1 System Manager role
- Administrator → System Manager role assignment
- 10 DocType metadata records
- 70 DocField records across all DocTypes
- 10 DocPerm records (full CRUD for System Manager on all DocTypes)

### HTTP Endpoints

| Route | Response |
|-------|----------|
| `GET /` | `{"app":"galaxy","status":"running"}` |
| `GET /health` | `{"status":"ok","app":"galaxy","database":"ok","site":"default.local"}` |
| `GET /api` | Framework identity JSON |
| `GET /api/version` | `{"name":"galaxy","engine":"Galaxy Engine","version":"0.0.1","stage":"bootstrap-core"}` |

### Technology Stack

- **Language:** Python 3.11+
- **CLI:** Typer
- **Database:** PostgreSQL 16 via SQLAlchemy 2.0 + psycopg 3
- **HTTP:** Starlette + Uvicorn
- **Auth:** passlib (bcrypt)
- **Build:** Hatchling
- **Lint:** Ruff

### Architecture Patterns

- One site = one database
- Metadata lives in database tables (not files)
- All seed operations are idempotent (skip-if-exists via `SELECT COUNT(*)`)
- Connection timeout set to 5 seconds for fast failure
- SQL reserved words (`read`, `write`, `create`, `delete`) quoted properly

### Acceptance Criteria

All 17 acceptance tests from the specification pass:

1. ✅ `galaxy install` completes without error
2. ✅ `sites/common_site_config.json` exists
3. ✅ `sites/default.local/site_config.json` exists
4. ✅ Database connection works
5. ✅ All 10 core tables exist
6. ✅ Administrator user with hashed password
7. ✅ System Manager role exists
8. ✅ Administrator has System Manager role
9. ✅ `core` installed app record
10. ✅ 6 module records
11. ✅ 10 DocType records
12. ✅ 70 DocField records
13. ✅ 10 DocPerm records
14. ✅ `galaxy doctor` returns OK
15. ✅ `galaxy start` runs server
16. ✅ `GET /health` returns correct JSON
17. ✅ `GET /api/version` returns correct JSON

### Files Created

```
cmd/galaxy/main.py
internal/__init__.py
internal/cli/__init__.py
internal/cli/app.py
internal/cli/doctor.py
internal/cli/install.py
internal/cli/reset.py
internal/cli/start.py
internal/config/__init__.py
internal/config/site_config.py
internal/bootstrap/__init__.py
internal/bootstrap/installer.py
internal/core/__init__.py
internal/db/__init__.py
internal/db/connection.py
internal/db/core_tables.py
internal/db/seed.py
internal/http/__init__.py
internal/http/server.py
internal/site/__init__.py
sites/common_site_config.json
sites/default.local/site_config.json
docker-compose.yml
tests/conftest.py
tests/test_config.py
tests/test_connection.py
tests/test_seed.py
docs/milestone-1-complete.md
.env.example
README.md
.gitignore
pyproject.toml
```

### What Comes Next (Milestone 2+)

- DocType Builder
- Dynamic CRUD API (Meta Query)
- Galaxy Desk UI
- Galaxy Studio visual builder
- Galaxy Cloud deployment
- Frappe/ERPNext plugin support
- Migration Planner
- Workflow engine
- Report builder
