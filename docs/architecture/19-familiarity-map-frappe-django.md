# 19 — Familiarity Map: Frappe & Django

## Purpose

Help developers from Frappe and Django communities understand Galaxy Framework by mapping familiar concepts to Galaxy equivalents.

---

## Frappe → Galaxy Concept Map

| Frappe Concept             | Galaxy Concept                           | Notes                                    |
|----------------------------|------------------------------------------|------------------------------------------|
| Bench                      | `galaxy` CLI                             | CLI-driven, no Node.js bench required    |
| bench init                 | `galaxy install`                         | Creates site config + database           |
| bench start                | `galaxy start`                           | Same pattern                             |
| bench new-site             | `galaxy bench create-site`               | Multi-site management                    |
| bench migrate              | `galaxy bench migration-status`          | Migration preview + apply                |
| bench backup               | `galaxy bench backup`                    | pg_dump wrapper                          |
| bench restore              | `galaxy bench restore`                   | pg_restore wrapper                       |
| bench install-app          | `galaxy bench install-app`               | Same concept                             |
| bench console              | Future: `galaxy console`                 | Python REPL with DB context              |
| Site                       | Site (same concept)                      | sites/<name>/ with config + backups      |
| App                        | App (same concept)                       | Registered in tabInstalled App           |
| Module Def                 | Module Def (same concept)                | Module registry, unchanged               |
| DocType                    | DocType (same concept)                   | Metadata-driven                          |
| DocField                   | DocField (same concept)                  | Field type dictionary expanded           |
| DocPerm                    | DocPerm (same concept)                   | Read/write/create/delete per role        |
| Role                       | Role (same concept)                      | System Manager, Guest, custom roles      |
| User                       | User (same concept)                      | tabUser with tenant_id                   |
| Has Role                   | Has Role (same concept)                  | Role assignment per user                 |
| Server Script              | Server Script                            | Stricter sandbox (13 blocked patterns)   |
| Report                     | Report                                   | SQL guard (14 dangerous keywords)        |
| Error Log                  | Error Log (same concept)                 | Auto-logged exceptions                   |
| Patch Log                  | Patch Log (same concept)                | Migration tracking                       |
| File                       | File (planned)                           | Local + S3 storage                       |
| Print Format               | Print Format (planned)                   | Jinja2 + PDF renderer                    |
| Workflow                   | Workflow (planned)                       | State machine engine                     |
| Comment                    | Comment (planned)                        | Activity log per document                |
| Communication              | Communication (planned)                  | Email integration                        |
| Notification Log           | Notification Log (planned)               | In-app notifications                     |
| Version                    | Version (planned)                        | Document versioning                      |
| Dashboard                  | Dashboard + Galaxy Desk                  | Modern operations view                   |
| Workspace                  | Optional module, not default             | Not the primary UI                       |
| Studio (Builder)           | Galaxy Studio                            | DocType builder, migration preview       |
| Desk                       | Galaxy Desk                              | Modern admin UI                          |
| frappe.get_doc             | `get_document()`                         | CRUD function (same pattern)             |
| frappe.db.get_value        | `repository.get_doctype()`               | Direct DB query helper                   |
| frappe.whitelist           | `@require_auth` + `_require_csrf()`     | API decorator pattern                    |
| frappe.session.user        | `get_session()` → `session["username"]`  | Session resolution                       |
| frappe.has_permission      | `authorize()`                            | DocPerm check                            |
| frappe.get_meta            | `get_doctype_fields()`                   | Metadata lookup                          |
| hooks.py                   | Future: hooks.py                         | App lifecycle hooks                      |
| apps.txt                   | Future: apps.txt                         | App registry                             |
| patches.txt                | Future: patches.txt                      | Patch migration (vs preview SQL)         |

## Django → Galaxy Concept Map

| Django Concept             | Galaxy Concept                           | Notes                                    |
|----------------------------|------------------------------------------|------------------------------------------|
| `django-admin startproject`| `galaxy install`                         | Interactive setup wizard                 |
| `python manage.py runserver`| `galaxy start`                          | Starlette/uvicorn server                 |
| `python manage.py shell`   | Future: `galaxy console`                 | REPL with app context                    |
| Django model               | DocType metadata                         | DB-stored, not code-defined              |
| `class Meta:`              | DocField metadata                        | Field definitions in tabDocField         |
| `CharField`                | DocField type "Data"                     | Single-line text                         |
| `TextField`                | DocField type "Text"                     | Multi-line text                          |
| `IntegerField`             | DocField type "Int"                      | Integer value                            |
| `FloatField`               | DocField type "Float"                    | Decimal value                            |
| `BooleanField`             | DocField type "Check"                    | Boolean (Check is Frappe legacy name)    |
| `DateTimeField`            | DocField type "Datetime"                 | Timestamp with timezone                  |
| `ForeignKey`               | DocField type "Link"                     | Reference to another DocType             |
| `ManyToManyField`          | DocField type "Table" (child table)      | Linked child table                       |
| `@property`                | DocField type "Read Only" or computed    | Server-side computed value               |
| Django admin list_display  | Galaxy Desk list view (metadata-driven)  | Columns from DocField metadata           |
| Django admin search_fields | Global search / list search              | Defined in DocType configuration         |
| Django admin list_filter   | Filter sidebar / query builder           | DocField-based filters                   |
| Django admin inlines       | Child table (Table field type)           | Inline child record editing              |
| Django forms               | FormView (metadata-driven)               | Fields rendered from DocField metadata   |
| Django ModelForm           | Auto-generated form from metadata        | Validation from DocField properties      |
| Django migrations          | `galaxy migration preview/apply`         | Preview SQL before applying              |
| `python manage.py migrate` | `galaxy bench migration-status`          | View pending schema changes              |
| Django permissions         | DocPerm + Role                           | Table-level, per-role permissions        |
| Django sites framework     | Site (same concept)                      | Multi-site via site_config               |
| Django settings.py         | `sites/<site>/site_config.json`          | JSON-based, env var override             |
| Django templates           | Jinja2 (same syntax)                     | Same template language                   |
| Django generic views       | Desk list/form views (metadata-driven)   | Auto-generated from metadata             |
| Django REST Framework      | Starlette API + optional FastAPI         | No forced serializers                    |
| `pip install django`       | `pip install galaxy-framework`           | Same pip install flow                    |

## Key Architectural Differences

### Frappe
- Uses Werkzeug (WSGI)
- MariaDB/PostgreSQL with custom ORM wrapper
- Workspace-first UI
- `hooks.py` for app lifecycle
- Python 3.10+ (legacy constraints)
- JS build via Vue 2 + webpack

### Galaxy
- Uses Starlette (ASGI) with optional FastAPI
- SQLAlchemy with PostgreSQL primary, SQLite dev
- Operations-first UI (Workspace optional)
- Metadata-driven lifecycle (hooks.py future)
- Python 3.11+
- Jinja2 + HTMX + vanilla JS (no SPA requirement)

### Django
- Uses WSGI (ASGI via Daphne optional)
- Django ORM (single DB backend focus)
- Admin UI (model registration)
- `models.py` is source of truth
- Middleware + URL routing pattern
- Large ecosystem of packages

## Migration Paths

### Frappe Developer Moving to Galaxy
1. Install: `pip install galaxy-framework && galaxy install`
2. Create DocTypes via Galaxy Studio (similar to Frappe DocType Builder)
3. Build Desk pages with metadata (no separate JS build needed)
4. Use server scripts for business logic (sandboxed)
5. Use CLI for site/app/bench management (similar to bench)
6. Deploy with PostgreSQL (familiar pg_dump/restore)

### Django Developer Moving to Galaxy
1. Install: `pip install galaxy-framework && galaxy install`
2. Understand metadata-first: no models.py, DocTypes are created in UI
3. Use Galaxy Desk for record management (similar to Django Admin)
4. Use galaxy CLI for manage.py-equivalent operations
5. Customize with Jinja2 templates (same as Django templates)
6. Add API endpoints with Starlette (similar to DRF but lighter)
7. No migration files to manage — preview SQL, apply when ready

## Shared Strengths

| Quality                    | Frappe | Django | Galaxy |
|----------------------------|--------|--------|--------|
| Rapid CRUD generation      | ✓      | ✓      | ✓      |
| Admin UI                   | ✓      | ✓      | ✓      |
| CLI tools                  | ✓      | ✓      | ✓      |
| Template engine            | ✓      | ✓      | ✓      |
| Permission system          | ✓      | ✓      | ✓      |
| Migration system           | ✓      | ✓      | ✓      |
| Multi-tenancy              | ✓      | ~      | ✓      |
| Modern async support       | ✗      | ~      | ✓      |
| Metadata-driven            | ✓      | ✗      | ✓      |
| SQLAlchemy                 | ✗      | ✗      | ✓      |
| pip install                | ✗      | ✓      | ✓      |
| Multiple DB backends       | ~      | ✓      | ✓      |
| Interactive installer      | ✗      | ~      | ✓      |
| OpenAPI docs               | ✗      | ~      | ~      |