# Galaxy Framework — User Instructions

## Stable Preferences

1. **One site = one database** — PostgreSQL 16 via Docker. Each site has its own database.
2. **Python core only** — No Go, no Node.js frontend for core framework.
   Desk UI uses Jinja2 templates with vanilla JS (no frameworks).
3. **SQLAlchemy Core** — Not ORM. `text()` for SQL, `mappings()` for row results.
4. **Starlette** — ASGI server with built-in routing, no FastAPI dependency.
5. **Typer CLI** — All framework commands via `python cmd/galaxy/main.py <command>`.
6. **PostgreSQL naming** — Tables are `tabDocType`, columns are `fieldname`, etc.
   SQL-reserved words (`"read"`, `"write"`, `"create"`, `"delete"`) always double-quoted.
7. **Idempotent seeds** — `SELECT COUNT(*)` check before inserting. Safe to re-run `galaxy install`.
8. **Preview before apply** — Migrations, CRUD, and data changes always preview first.
9. **No code generation** — Metadata is interpreted at runtime, never compiled.
10. **Minimal dependencies** — Prefer stdlib. Only add dependencies when necessary.

## Current Active Work
- Milestone 5: Core CRUD Engine (next)
- Migration system complete for CREATE TABLE

## Always Check
- `ROADMAP.md` before starting work
- `VISION.md` for architectural principles
- `AGENTS.md` for file paths and conventions
- `internal/http/server.py` for existing routes before adding new ones
- `internal/core/` for existing modules before creating new ones

## Pre-commit Checklist
1. `python -m compileall internal`
2. `ruff check .`
3. `python cmd/galaxy/main.py doctor`
4. Start server and test new endpoints
5. Stop server (PowerShell: `Stop-Process -Id <PID> -Force`)
