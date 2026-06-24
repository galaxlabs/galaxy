# Galaxy Framework Agent Skill

## Description
Build and extend the Galaxy Framework — a metadata-driven full-stack low-code business application framework using Python, PostgreSQL, Starlette, and SQLAlchemy Core.

## Triggers
- User mentions "Galaxy Framework", "galaxy", "Milestone", or the project at `E:\Projects\galaxy\`
- User asks to build DocType Builder, CRUD engine, migration system, or Desk UI features
- User reports bugs in `galaxy install/doctor/start/reset` commands

## Project Structure

```
E:\Projects\galaxy\
├── ai/agents/galaxy/        ← This skill + agent instructions
├── cmd/galaxy/main.py       ← CLI entry point (Typer)
├── internal/
│   ├── bootstrap/           ← Installer, doctor, reset
│   ├── cli/                 ← CLI command definitions
│   ├── config/              ← Site config loading
│   ├── core/                ← Business logic:
│   │   ├── api.py           ←   Starlette API handlers
│   │   ├── repository.py    ←   Read-only SQL repository
│   │   ├── builder.py       ←   DocType Builder validation
│   │   ├── builder_repository.py  ←   Save metadata
│   │   ├── migration_planner.py   ←   Migration planning
│   │   └── migration_applier.py   ←   Safe apply migrations
│   ├── db/                  ← Connection, DDL, seed data
│   └── http/                ← Server, routes, templates, CSS
├── sites/                   ← Site configs
├── tests/                   ← Pytest tests
├── docs/                    ← Milestone documentation
├── AGENTS.md                ← Agent routing rules
├── ROADMAP.md               ← Milestone roadmap
└── VISION.md                ← Long-term vision
```

## Workflow Steps

### 1. Understand the Current State
- Read `ROADMAP.md` for milestone progress
- Read `VISION.md` for principles
- Read `internal/http/server.py` for existing routes
- Read relevant module in `internal/core/` before making changes

### 2. Making Changes
- Follow the patterns in existing code (same imports, error handling, naming)
- Use `_get_engine()` pattern for database access
- Use `engine.begin()` for transactional writes
- Add routes to `internal/http/server.py` after builder routes
- Add API handlers to `internal/core/api.py`
- Add repository functions to `internal/core/repository.py`

### 3. Verification
```bash
python -m compileall internal        # No compile errors
ruff check .                         # No lint errors
python cmd/galaxy/main.py doctor     # DB health OK
pytest tests/                        # All tests pass
```

### 4. Manual Testing
```bash
python cmd/galaxy/main.py start      # Start server on :8080
curl http://127.0.0.1:8080/health    # Health check
# Run specific endpoint tests
```

## Key Conventions

### Database
- All DocType tables prefixed `tab` (e.g., `tabDocType`, `tabCustomer`)
- Engine via `_get_engine()` pattern in each layer
- Table/column names with spaces or SQL-reserved words double-quoted
- `SELECT COUNT(*)` checks before seed inserts for idempotency

### API
- Route pattern: `/api/<domain>/<resource>/<action>`
- Return `{"data": ...}` for success, `{"error": "..."}` for errors
- HTTP 404 for not-found, 409 for conflict, 400 for validation errors, 500 for exceptions
- URL-decode path params with `urllib.parse.unquote()`

### Templates
- Extend `base.html` for desk pages
- Use `{% block content %}` for page body
- Use `{% block title %}` and `{% block heading %}` for page title/header
- CSS classes: `.data-table`, `.detail-section`, `.badge-*`, `.btn`, `.btn-primary`, `.sql-block`

### Code Style
- No comments in code (unless asked)
- Type hints on function parameters
- Error handling: try/except with `JSONResponse({"error": str(e)}, status_code=500)`
- No external dependencies beyond Starlette, SQLAlchemy, psycopg, Typer, Jinja2, uvicorn, bcrypt, passlib, pytest

## Related Skills
- `frappe-doctype-development` — DocType schema patterns (naming, fields, permissions reference)
- `frappe-api-development` — API patterns reference
- `frappe-desk-customization` — Desk UI patterns reference
