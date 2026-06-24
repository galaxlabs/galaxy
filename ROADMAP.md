# Galaxy Framework — Roadmap

## Milestone 1 — Bootstrap Core ✅
- [x] `galaxy install` — create core tables, seed data
- [x] `galaxy doctor` — health check
- [x] `galaxy start` — Starlette HTTP server
- [x] `galaxy reset` — drop and recreate tables
- [x] 10 core tables with seed data
- [x] README quickstart, `.env.example`
- [x] 13 pytest tests
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

## Milestone 5 — Core CRUD Engine 🏗️ (Next)
- [ ] Generic CRUD repository for physical DocType tables
- [ ] `GET /api/crud/{doctype}` — list records
- [ ] `GET /api/crud/{doctype}/{name}` — single record
- [ ] `POST /api/crud/{doctype}` — create record
- [ ] `PUT /api/crud/{doctype}/{name}` — update record
- [ ] `DELETE /api/crud/{doctype}/{name}` — soft delete
- [ ] Record list view in Desk UI (auto-generated from metadata)
- [ ] Record form view in Desk UI (auto-generated from metadata)

## Milestone 6 — Permission Engine
- [ ] Role-based DocType access (read/create/write/delete)
- [ ] Permission checks in CRUD API
- [ ] Row-level permission (user matches owner field)
- [ ] Permission UI in Desk

## Milestone 7 — Server Scripting
- [ ] Python server scripts on DocType events (before_save, after_save, on_submit, etc.)
- [ ] Script execution engine
- [ ] Script editor in Desk
- [ ] `frappe`-like API: `frappe.get_doc()`, `frappe.db`, etc.

## Milestone 8 — Report Builder
- [ ] Query Report (raw SQL)
- [ ] Script Report (Python + JS)
- [ ] Report builder UI
- [ ] Dashboard cards

## Milestone 9+ — Platform
- [ ] Workspace builder
- [ ] Notification engine
- [ ] Background jobs
- [ ] Multi-site management
- [ ] Plugin system

## Current Status

| Metric | Value |
|--------|-------|
| Python source files | ~15 in `internal/` |
| Core tables | 10 |
| DocTypes (seeded) | 10 + 2 custom (Customer, Supplier) |
| API endpoints | 16 routes |
| CLI commands | `install`, `doctor`, `start`, `reset` |
| Frontend | 5 Jinja2 templates + CSS |
| Tests | 13 pytest |
| Docker | PostgreSQL 16 |
| Physical tables created | `tabCustomer`, `tabSupplier` |
