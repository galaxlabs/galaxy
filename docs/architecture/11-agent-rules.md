# Agent Rules

## Purpose

Rules for AI agents (Claude, GPT, Cursor, Copilot, etc.) working on the Galaxy Framework codebase.

## 1. No Random Features

Do not add features outside the current milestone. Work in this order:

1. Verify current M1–M12 implementation
2. Freeze architecture documents
3. Create missing dictionaries/specs
4. Refactor package/app structure if needed
5. Harden tests
6. Only then continue new features

## 2. Project Identity

- Galaxy Framework is a **Python metadata-driven business application framework**
- Inspired by Frappe, Django Admin, Flask, Odoo, and Tryton
- It is **NOT** a Frappe clone
- It is **NOT** an ERPNext fork
- It is **NOT** a no-code platform (it is developer-first)

## 3. No Go Yet

- Do NOT switch to Go now
- Do NOT create Gogal code
- Go will be used later only after the Python architecture is proven and documented
- See `docs/architecture/10-python-to-go-translation-dictionary.md` for the porting guide

## 4. Architecture Principles

### Metadata is Source of Truth
- DocType metadata creates: database table, fields, validation, permissions, CRUD API, Desk form, Desk list, report base, migration plan
- SQLAlchemy Core is only an implementation helper — NOT the source of truth

### PostgreSQL First
- No MySQL/MariaDB until PostgreSQL behavior is stable
- See `docs/architecture/05-postgres-mysql-dialect-differences.md`

### No Hard Foreign Keys in v1
- Link fields store target document name as text
- No `REFERENCES` constraint
- See `docs/architecture/06-link-and-foreign-key-policy.md`

### Safe Migrations Only
- `CREATE TABLE` and `ADD COLUMN` are auto-approved
- All other DDL requires preview + confirmation
- Frontend must never send raw SQL
- See `docs/architecture/07-migration-safety-rules.md`

### Tenant Isolation
- Every tenant-scoped query must be tested for isolation
- See `docs/architecture/09-tenant-models.md`

## 5. Security Rules (Never Weaken)

Keep all M10 security:
- Route protection via `RequireSessionMiddleware`
- CSRF HMAC tokens on all POST/PUT/DELETE
- 13 blocked script patterns, 10 blocked modules
- 14 dangerous SQL keywords blocked, comment stripping
- Safe error messages (no stack traces to users)
- Login rate limiting (5 attempts / 300s)
- Secure config defaults in `common_site_config.json`
- No auth bypass headers (`X-Galaxy-User` removed)
- All dangerous actions logged via `log_security_event()`

## 6. Testing Rules

Before any feature work, run:
```bash
python -m compileall internal
ruff check .
python cmd/galaxy/main.py doctor
pytest tests/
```

All must pass. Fix failures before proceeding.

## 7. Code Style

- Line length: 110 (configured in pyproject.toml)
- Use double quotes for strings
- Python 3.11+ target
- Typed signatures preferred but not strictly enforced
- No comments on code that is self-documenting
- No emojis in code or documentation unless user explicitly asks

## 8. Import Rules

- `internal/db/` must never import from `internal/core/` or `internal/http/`
- `internal/core/` must never import from `internal/http/`
- `internal/http/` may import from `internal/core/` and `internal/db/`
- Circular imports are forbidden. Use lazy (function-level) imports if needed
- The tenant module (`internal/core/tenant.py`) must use lazy imports for `require_auth` and `_require_csrf` to avoid circular imports with `internal/core/api.py`

## 9. State Management

- Server state is process-local (in-memory)
  - Rate limit counters
  - CSRF secrets
  - Tenant context vars
- State resets on server restart
- Not shared across multiple workers (future: Redis)
- Use `contextvars.ContextVar` for request-scoped state (like `current_tenant`)

## 10. Documentation Rules

- Architecture decisions go in `docs/architecture/`
- Each milestone acceptance goes in `docs/`
- README.md is for quick start only
- AGENTS.md is for agent routing
- Do not create README files inside code directories

## 11. Verification Commands

```bash
# Compile check
python -m compileall internal

# Lint
ruff check .

# Doctor
python cmd/galaxy/main.py doctor

# Tests
pytest tests/

# Quick server test
python cmd/server/main.py &
curl http://127.0.0.1:8080/health
kill %1
```

## 12. Agent Routing

See `AGENTS.md` in the project root for routing rules:
- `galaxy` → use `ai/agents/galaxy/SKILL.md`
- Frappe/ERPNext → use Frappe skills
- General programming → use general skills