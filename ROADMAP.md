# Galaxy Framework — Roadmap

## Milestone 1 — Bootstrap Core ✅
- [x] `galaxy install` — create core tables, seed data
- [x] `galaxy doctor` — health check
- [x] `galaxy start` — Starlette HTTP server
- [x] `galaxy reset` — drop and recreate tables
- [x] 12 core tables with seed data
- [x] README quickstart, `.env.example`
- [x] 30 pytest tests
- [x] Project rename: `galaxy-framework` → `galaxy`

## Milestone 2 — Core Metadata Read API + Desk ✅
- [x] Read-only repository layer (8 SQL functions)
- [x] 8 core API endpoints (`/api/core/*`)
- [x] Desk UI with Jinja2 templates (base layout, sidebar, summary cards)
- [x] DocType list and detail pages
- [x] 19 acceptance tests

## Milestone 3 — DocType Builder ✅
- [x] `POST /api/builder/doctype/preview` — validate + build JSON
- [x] `POST /api/builder/doctype/save` — persist metadata to DB
- [x] Desk UI: DocType Builder form with fields grid
- [x] Migration status (`pending`/`applied`) on metadata API
- [x] Migration status column + badge in Desk UI

## Milestone 4 — Migration Preview Engine ✅
- [x] Migration planner: `plan_doctype_migration()`, `generate_create_table_plan()`
- [x] `GET /api/migration/doctype/{name}/preview`
- [x] Migration Preview panel in Desk UI
- [x] `POST /api/migration/doctype/{name}/apply` — safe CREATE TABLE only
- [x] "Apply Migration" button in Desk UI with confirm

## Milestone 5 — Core CRUD Engine ✅
- [x] Generic CRUD repository (`create_document`, `list_documents`, `get_document`, `update_document`, `delete_document`)
- [x] `GET /api/resource/{doctype}` — list records
- [x] `GET /api/resource/{doctype}/{name}` — single record
- [x] `POST /api/resource/{doctype}` — create record
- [x] `PUT /api/resource/{doctype}/{name}` — update record
- [x] `DELETE /api/resource/{doctype}/{name}` — delete record
- [x] Record list view in Desk UI (auto-generated from metadata)
- [x] Record form view in Desk UI (auto-generated from metadata)
- [x] 17 CRUD acceptance tests

## Milestone 6 — Permission Engine ✅
- [x] Role-based DocType access (read/create/write/delete)
- [x] Permission checks in CRUD API (via `X-Galaxy-User` header)
- [x] `authorize()` function with user role lookup
- [x] Permission UI in Desk (existing table in doctype_detail)

## Milestone 7 — Server Scripting ✅
- [x] Python server scripts on DocType events (before_save, after_save, before_delete, after_delete, on_load)
- [x] Script execution engine (`internal/core/script_engine.py`)
- [x] Script editor in Desk (new/edit form with code textarea)
- [x] `frappe`-like API: `frappe.get_doc()`, `frappe.db.sql()`, `frappe.log_error()`
- [x] Script hooks integrated into CRUD operations

## Milestone 8 — Report Builder ✅
- [x] Query Report (raw SQL) — `GET /api/report/{name}`
- [x] Script Report (Python) — `GET /api/report/{name}`
- [x] Report Desk UI — list, detail with Run Report button
- [x] Query validation (only SELECT allowed)

## Milestone 9+ — Platform 🏗️
- [ ] Workspace builder
- [ ] Notification engine
- [ ] Background jobs
- [ ] Multi-site management
- [ ] Plugin system
- [ ] Auth/sessions (JWT login)
- [ ] Soft delete with docstatus
- [ ] Row-level permissions
- [ ] Dashboard cards
- [ ] Script Report UI builder

## Current Status

| Metric | Value |
|--------|-------|
| Python source files | ~25 in `internal/` |
| Core tables | 12 (6 new M7/M8) |
| DocTypes (seeded) | 12 core + custom (Customer, Supplier) |
| API endpoints | 22 routes |
| CLI commands | `install`, `doctor`, `start`, `reset` |
| Frontend | 8 Jinja2 templates + CSS |
| Tests | 30 pytest |
| Docker | PostgreSQL 16 |
| Physical tables created | `tabCustomer`, `tabSupplier` |
