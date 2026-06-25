# Galaxy

Metadata-driven full-stack low-code business application framework.

Built with Python, PostgreSQL, Starlette, and SQLAlchemy.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16 (Docker recommended)
- Docker (optional but recommended)

### Setup

```powershell
# 1. Start PostgreSQL via Docker
docker compose up -d

# 2. Install dependencies
pip install -e .

# 3. Install Galaxy site
python cmd\galaxy\main.py install

# 4. Verify installation
python cmd\galaxy\main.py doctor

# 5. Start the server
python cmd\galaxy\main.py start
```

### Verify

```powershell
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/api/version
```

### Reset

```powershell
python cmd\galaxy\main.py reset
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `galaxy install` | Bootstrap a Galaxy site |
| `galaxy doctor`  | Check installation health |
| `galaxy start`   | Start the HTTP server |
| `galaxy reset`   | Drop and recreate core tables |

## Status

**Milestones 1–8 complete.** Fully functional: metadata engine, DocType Builder, migration engine, CRUD API + Desk UI, permission engine, server scripting, and report builder.

## Project Structure

```
galaxy/
├── cmd/galaxy/main.py              # CLI entry point
├── internal/
│   ├── bootstrap/                  # Installer and doctor
│   ├── cli/                        # Typer CLI commands
│   ├── config/                     # Site configuration
│   ├── core/                       # Core business logic
│   │   ├── api.py                  # API handlers
│   │   ├── crud.py                 # CRUD engine
│   │   ├── permissions.py          # Role-based access control
│   │   ├── report_engine.py        # Report builder
│   │   └── script_engine.py        # Server scripting
│   ├── db/                         # Database layer
│   │   ├── connection.py           # SQLAlchemy engine (pooled)
│   │   ├── core_tables.py          # 12 core DDLs
│   │   ├── metadata.py             # DocType metadata queries
│   │   ├── repository.py           # DocType/field resolvers
│   │   ├── seed.py                 # Idempotent data seeding
│   │   └── migration.py            # ALTER TABLE migration
│   └── http/                       # Starlette HTTP server
│       ├── server.py               # 22 routes, Starlette app
│       ├── static/                 # CSS/JS assets
│       └── templates/              # Jinja2 templates
│           ├── base.html           # Sidebar + layout
│           ├── doctype_detail.html # DocType builder form
│           ├── doctype_list.html   # DocType list
│           ├── resource_list.html  # Record list
│           ├── resource_detail.html# Record detail
│           ├── server_scripts.html # Script list
│           ├── server_script_form.html
│           ├── reports.html        # Report list
│           └── report_detail.html  # Report runner
├── sites/                          # Site configs
├── tests/                          # Pytest test suite
│   ├── test_seed.py                # 13 seed/metadata tests
│   └── test_crud.py                # 17 CRUD tests
└── docs/                           # Milestone documentation
```

## Milestones

| # | Name | Status |
|---|------|--------|
| 1 | Bootstrap Core | Done |
| 2 | DocType Builder | Done |
| 3 | Metadata API + Desk UI | Done |
| 4 | Migration Engine | Done |
| 5 | Core CRUD Engine | Done |
| 6 | Permission Engine | Done |
| 7 | Server Scripting | Done |
| 8 | Report Builder | Done |
| 9+ | Platform Features (auth, workspaces, jobs, notifications, dashboards, plugins) | Pending |
