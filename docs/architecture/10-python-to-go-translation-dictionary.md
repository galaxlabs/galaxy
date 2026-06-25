# Python to Go Translation Dictionary

## Purpose

Document every dynamic feature of the Python framework with its database behavior, edge cases, tests, and possible Go implementation. This dictionary exists to verify the Python architecture is proven before any Go rewrite begins.

## 1. CRUD Engine

### Python Implementation
- `create_document(doctype, payload)` → dynamic INSERT via SQLAlchemy Core `text()`
- `get_document(doctype, name)` → dynamic SELECT with `text()`
- `list_documents(doctype, limit, offset)` → dynamic SELECT with LIMIT/OFFSET
- `update_document(doctype, name, payload)` → dynamic UPDATE with SET clauses
- `delete_document(doctype, name)` → dynamic DELETE

### Database Behavior
- Reads `tabDocType` + `tabDocField` to build SQL column list
- Constructs parameterized SQL with `:param` placeholders
- No ORM — uses `sqlalchemy.text()` for raw SQL execution
- Tenant filtering via `_tenant_where()` appends `AND "tenant_id" = :_tenant_id`

### Edge Cases
- Unknown fields in payload → rejected
- Required fields missing → rejected
- Hidden/read-only fields in payload → rejected
- Duplicate name → IntegrityError caught, returned as error
- Coercion errors (int/float/JSON) → ValueError caught, returned as error
- Tenant isolation → document not visible across tenants

### Tests
- `test_crud.py`: 17 tests covering create, validate, list, get, duplicate, coercion
- `test_tenant_isolation.py`: 6 tests covering cross-tenant list/get/update/delete isolation

### Go Implementation
- Replace SQLAlchemy with `database/sql` + `lib/pq` (PostgreSQL driver)
- Dynamic SQL construction using string building with parameterized queries
- No ORM equivalent — same raw SQL approach
- Use Go's `text/template` or `strings.Builder` for SQL generation
- Column list and field validation from metadata cache (in-memory map)

### Risk Level: Low
SQL is simple and parameterized. Go's `database/sql` handles this well.

---

## 2. DocType Builder

### Python Implementation
- `validate_doctype_payload(payload)` → validates field definitions
- `build_doctype_json(doctype_name, fields)` → builds metadata JSON
- `save_doctype_metadata(doctype_json, fields)` → writes to `tabDocType` + `tabDocField`

### Database Behavior
- Writes to two tables in sequence (DocType record + multiple DocField records)
- Uses `etcd` library or similar for row-level locking (not currently implemented)
- No transaction wrapping around the pair (future enhancement)

### Edge Cases
- Invalid field types → rejected
- Missing required DocType properties → rejected
- Duplicate field names → rejected
- Reserved field names (`name`, `idx`) → rejected

### Tests
- Builder tests in `test_crud.py` (indirect via Supplier DocType creation)

### Go Implementation
- Same two-step INSERT logic
- Use Go structs for metadata model
- Transaction wrapping via `db.Begin()` / `tx.Commit()`
- JSON serialization via `encoding/json`

### Risk Level: Low

---

## 3. Migration Engine

### Python Implementation
- `plan_doctype_migration(doctype_name)` → reads metadata + current schema → generates SQL plan
- `apply_doctype_migration(doctype_name)` → executes safe DDL (CREATE TABLE, ADD COLUMN)

### Database Behavior
- Reads `tabDocType` + `tabDocField` for target schema
- Queries `information_schema.columns` for current schema
- Generates `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE ADD COLUMN IF NOT EXISTS`
- Does NOT modify or drop existing columns

### Edge Cases
- Table already exists with all columns → no-op
- Table already exists with some columns → adds missing columns
- Doctype not saved yet → error
- Illegal table name → error

### Tests
- Migration preview in auth tests
- Migration status in bench tests

### Go Implementation
- Same `information_schema.columns` introspection
- SQL generation via `fmt.Sprintf` or `strings.Builder`
- Use Go's `database/sql` with parameterized DDL (DDL cannot use parameters, so use fmt)

### Risk Level: Medium
DDL varies by database driver. Some DDL cannot use parameterized queries, requiring careful escaping.

---

## 4. Permission Engine

### Python Implementation
- `get_user_roles(username)` → `SELECT role FROM "tabHas Role" WHERE parent = :username`
- `check_permission(doctype, role, perm_type)` → `SELECT {perm_type} FROM "tabDocPerm" WHERE parent = :doctype AND role = :role`
- `authorize(doctype, username, perm_type)` → combines above
- System Manager role always returns True

### Database Behavior
- Two simple SELECT queries per authorization
- No caching currently

### Edge Cases
- Unknown username → empty role list → denied
- Unknown doctype → no perm record → denied (System Manager bypass)
- No tabDocPerm record for role → denied

### Tests
- `test_auth.py`: permission tests (authorize, get_user_roles, user_has_role)

### Go Implementation
- Same SELECT queries
- In-memory cache with TTL for role/perm lookups
- System Manager bypass as a simple string comparison

### Risk Level: Very Low

---

## 5. Auth/Session

### Python Implementation
- `verify_password(username, password)` → bcrypt verify against `tabUser`
- `create_session(username)` → generates random token, inserts into `tabSession`
- `get_session(token)` → SELECT from `tabSession` JOIN `tabUser`, checks expiry
- `delete_session(token)` → DELETE from `tabSession`
- Session expiry: 24 hours, checked in Python (not DB)

### Database Behavior
- bcrypt hash stored in `password_hash` column
- Session token stored as VARCHAR(255) with UNIQUE constraint
- `expires_at` timestamp compared against `datetime.now(UTC)` in Python

### Edge Cases
- Wrong password → None
- Expired session → treated as non-existent
- Disabled user → session denied even if token valid
- Cross-tenant session → filtered by `tenant_id`

### Tests
- `test_auth.py`: login, logout, session lifecycle, expiry

### Go Implementation
- Use `golang.org/x/crypto/bcrypt` for password verification
- `crypto/rand` for token generation
- Same SQL queries via `database/sql`
- Session expiry check in Go time logic

### Risk Level: Very Low

---

## 6. Server Scripts

### Python Implementation
- `run_scripts(doctype, event, doc_data)` → SELECTs scripts from `tabServer Script`, `exec()` each
- `FrappeAPI` class provides a safe sandbox (`frappe.db.get_value()`, `frappe.db.set_value()`, etc.)
- `FrappeDB` class wraps DB operations for scripts
- `BLOCKED_PATTERNS` (13) and `BLOCKED_MODULES` (10) for dangerous code detection
- Scripts run as hooks: `before_save`, `after_save`, `before_delete`, `after_delete`, `on_load`

### Database Behavior
- Reads script code from `tabServer Script`
- Script code is Python text, not compiled
- `exec()` in Python is inherently unsafe — blocked patterns mitigate

### Edge Cases
- Empty script → skip
- Script with blocked pattern → error
- Script syntax error → caught and returned
- Script runtime error → caught and returned
- Infinite loop → no protection (future: timeout)

### Tests
- `test_security.py`: dangerous code pattern tests

### Go Implementation
- Go has no `exec()` equivalent for user code
- Options: (a) embed Lua or JavaScript VM, (b) use WebAssembly, (c) use Go plugin system
- Riskier than Python due to limited sandboxing options
- Consider embedding a Lua interpreter (`go-lua`) for user scripts

### Risk Level: High
Go cannot dynamically execute Go code. Requires embedding another language runtime.

---

## 7. Report Builder

### Python Implementation
- `run_query_report(report)` → validates SQL (14 dangerous keywords blocked), executes SELECT
- `run_script_report(report)` → exec() Python to generate results

### Database Behavior
- Query reports: arbitrary SELECT queries on the site DB
- SQL validation via `_validate_query_safe()` — blocks INSERT/UPDATE/DELETE/DROP/ALTER/etc.
- Comment stripping before keyword check (blocks `DR/**/OP` type evasion)

### Edge Cases
- Empty query → error
- Dangerous operation → blocked with specific error
- SQL syntax error → caught and returned
- Comment-based evasion → comment stripped before validation

### Tests
- `test_security.py`: SQL validation tests (block dangerous keywords)

### Go Implementation
- Query reports: same SELECT execution with SQL validation (regex-based)
- Script reports: same Lua/VM embedding challenge as server scripts
- SQL validation port: Go regexp is sufficient

### Risk Level: Medium (query), High (script)

---

## 8. CSRF Protection

### Python Implementation
- Token generated as HMAC-SHA256(session_token, csrf_secret)
- Token stored in cookie `galaxy_csrf`
- Validated on all POST/PUT/DELETE via `X-CSRF-Token` header
- `_require_csrf(request)` → verifies HMAC matches

### Database Behavior
- No DB storage for CSRF — fully HMAC-derived
- `csrf_secret` read from `common_site_config.json` on each call

### Edge Cases
- Missing token → 403
- Token mismatch → 403
- Token from wrong session → 403
- Token expired (session expired) → 403
- GET/HEAD requests → not checked

### Tests
- `test_security.py`: CSRF tests

### Go Implementation
- Same HMAC logic using `crypto/hmac` + `crypto/sha256`
- Cookie reading via `net/http` request
- Header reading via request header
- Much simpler than Python — Go's stdlib has everything needed

### Risk Level: Very Low

---

## 9. Login Rate Limiting

### Python Implementation
- In-memory dict: `{key: [attempt_count, window_start]}`
- Key: `IP:username` for per-user, or `IP` for per-IP
- Default: 5 attempts per 300-second window
- Configurable via `common_site_config.json`

### Database Behavior
- No DB storage — fully in-memory
- Resets on server restart
- Not shared across multiple workers

### Edge Cases
- First attempt from new IP → allowed
- 6th attempt within window → blocked
- Attempt after window expires → counter resets
- Rate limiting disabled via config → no-op
- Distributed attack across many IPs → not caught (no shared state)

### Tests
- `test_security.py`: rate limit tests

### Go Implementation
- In-memory sync.Map with periodic cleanup goroutine
- Better concurrency than Python dict
- Still not shared across processes — Redis needed for distributed rate limiting
- Use `sync.Map` or `map[string]*RateEntry` with `sync.Mutex`

### Risk Level: Very Low (same pattern, better concurrency)

---

## 10. Tenant Isolation

### Python Implementation
- `current_tenant` context var (thread-local)
- Middleware sets tenant from request
- `_tenant_where()` appends `"tenant_id" = :_tenant_id` to CRUD queries
- Auth functions filter by tenant_id

### Database Behavior
- `tenant_id VARCHAR(255) NOT NULL DEFAULT 'Default'` on tenant-scoped tables
- Queries include `AND tenant_id = :tenant_id` for both reads and writes

### Edge Cases
- No tenant header → "Default" tenant
- Unknown subdomain → "Default" tenant
- Cross-tenant name collision → allowed (different tenant_ids)
- System tables → no tenant_id filtering

### Tests
- `test_tenant.py`: 16 tests
- `test_tenant_isolation.py`: 6 tests

### Go Implementation
- Use `context.Context` instead of `contextvars`
- Pass context through request chain
- Same SQL filtering approach
- Go's `context.Context` is more idiomatic and safer than Python's contextvars for this use case

### Risk Level: Very Low

---

## Summary

| Feature | Risk | Go Difficulty | Notes |
|---------|------|--------------|-------|
| CRUD Engine | Low | Medium | Dynamic SQL building requires care |
| DocType Builder | Low | Low | Simple INSERTs |
| Migration Engine | Medium | Medium | DDL portability |
| Permission Engine | Very Low | Very Low | Simple queries |
| Auth/Session | Very Low | Very Low | Direct bcrypt port |
| Server Scripts | High | High | No Go exec() equivalent |
| Report Builder | Medium | Medium-High | Script reports same as scripts |
| CSRF | Very Low | Very Low | HMAC is stdlib |
| Rate Limiting | Very Low | Very Low | In-memory map |
| Tenant Isolation | Very Low | Very Low | Context-based filtering |

**Only port when:**
1. Python architecture is stable and tested (freeze)
2. All 11 architecture docs are approved
3. Server Scripts and Script Reports have a proven Go embedding strategy (Lua/JS/WASM)
4. The first Go service is a small, bounded component (e.g., CRUD API for a single DocType)