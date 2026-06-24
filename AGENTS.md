# Galaxy Framework — Agent Routing

This file defines how AI agents work with the Galaxy Framework codebase.

## Architecture

Galaxy Framework is a Python/PostgreSQL metadata-driven low-code framework.
Code lives in `E:\Projects\galaxy\`. The active agents directory is `ai/agents/`.

## Agent Types

| Agent | Trigger | Files |
|-------|---------|-------|
| **galaxy** | Any Galaxy Framework task | `ai/agents/galaxy/SKILL.md`, `USER_INSTRUCTIONS.md` |

## Routing Rules

1. **Galaxy Framework tasks** → use `ai/agents/galaxy/SKILL.md`
2. **Frappe/ERPNext tasks** → use Frappe skills from `~/.agents/skills/frappe-skills/`
3. **Other projects** → refer to `E:\AGENTS.md` for routing

## Project Conventions

- **Python 3.11+** — use stdlib where possible, minimal dependencies
- **PostgreSQL 16** — all DocType data in physical tables prefixed `tab`
- **SQLAlchemy Core** — for connection management and parameterized queries (not ORM)
- **Starlette** — ASGI HTTP server with Jinja2 templates
- **Typer** — CLI framework
- **psycopg 3** — PostgreSQL driver
- **pytest** — test framework (no unittest)
- **ruff** — linter and formatter

## Important Paths

| Path | Purpose |
|------|---------|
| `internal/core/` | Business logic, repositories, builders |
| `internal/db/` | Database connection and DDL |
| `internal/http/` | HTTP server, routes, templates |
| `internal/http/templates/` | Jinja2 templates |
| `internal/http/static/` | CSS and static assets |
| `internal/config/` | Site configuration loading |
| `internal/cli/` | CLI command definitions |
| `internal/bootstrap/` | Installer, doctor, reset |
| `cmd/galaxy/main.py` | CLI entry point |
| `sites/*/site_config.json` | Site-specific configuration |
| `tests/` | Pytest tests |
| `docs/` | Milestone documentation |

## Verification Commands

```bash
python -m compileall internal        # Compile check all Python files
ruff check .                         # Lint
python cmd/galaxy/main.py doctor     # Health check
pytest tests/                        # Run tests
```
