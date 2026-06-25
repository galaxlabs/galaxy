# 18 — Package Folder Map

## Target Structure

```text
E:\Projects\galaxy\
├── apps\
│   └── galaxy\
│       └── galaxy\           ← import as "galaxy" (via hatchling package mapping)
│           ├── __init__.py
│           ├── config.py
│           │
│           ├── auth\          ← Authentication & sessions
│           │   ├── __init__.py
│           │   ├── password.py
│           │   ├── session.py
│           │   ├── api.py
│           │   └── middleware.py
│           │
│           ├── bench_manager\ ← Site & app management (moved from internal/bench)
│           │   ├── __init__.py
│           │   ├── api.py
│           │   ├── sites.py
│           │   ├── backups.py
│           │   ├── apps.py
│           │   └── services.py
│           │
│           ├── cli\           ← CLI commands
│           │   ├── __init__.py
│           │   ├── main.py
│           │   ├── install.py
│           │   ├── doctor.py
│           │   ├── start.py
│           │   ├── migrate.py
│           │   ├── backup.py
│           │   └── restore.py
│           │
│           ├── core\          ← Core metadata engine + API
│           │   ├── __init__.py
│           │   ├── api.py
│           │   ├── repository.py
│           │   └── doctype\
│           │       ├── __init__.py
│           │       ├── builder.py
│           │       └── builder_repository.py
│           │
│           ├── crud\          ← Dynamic CRUD engine
│           │   ├── __init__.py
│           │   ├── engine.py
│           │   └── api.py
│           │
│           ├── db\            ← Database connection + core tables
│           │   ├── __init__.py
│           │   ├── connection.py
│           │   ├── core_tables.py
│           │   ├── seed.py
│           │   └── dialects\
│           │       ├── __init__.py
│           │       ├── postgres.py
│           │       ├── sqlite.py
│           │       ├── mysql.py
│           │       └── mariadb.py
│           │
│           ├── desk\          ← Galaxy Desk UI
│           │   ├── __init__.py
│           │   ├── routes.py
│           │   ├── layout.py
│           │   ├── navigation.py
│           │   ├── listview.py
│           │   ├── formview.py
│           │   ├── dashboard.py
│           │   ├── components\  ← UI component library
│           │   │   ├── button.html
│           │   │   ├── card.html
│           │   │   ├── modal.html
│           │   │   └── ...      (per component)
│           │   ├── templates\   ← Desk Jinja2 templates
│           │   └── static\      ← Desk CSS/JS
│           │
│           ├── email\         ← Email sending
│           │   ├── __init__.py
│           │   ├── sender.py
│           │   ├── templates.py
│           │   └── queue.py
│           │
│           ├── files\         ← File storage abstraction
│           │   ├── __init__.py
│           │   ├── storage.py
│           │   ├── local.py
│           │   ├── s3.py
│           │   ├── upload.py
│           │   └── permissions.py
│           │
│           ├── installer\     ← Guided setup wizard
│           │   ├── __init__.py
│           │   ├── wizard.py
│           │   ├── prompts.py
│           │   ├── database.py
│           │   ├── admin_user.py
│           │   └── site_config.py
│           │
│           ├── integrations\  ← Third-party integrations
│           │   └── __init__.py
│           │
│           ├── jobs\          ← Background jobs + scheduler
│           │   ├── __init__.py
│           │   ├── queue.py
│           │   ├── scheduler.py
│           │   ├── worker.py
│           │   └── job_log.py
│           │
│           ├── migration\     ← Schema migration engine
│           │   ├── __init__.py
│           │   ├── planner.py
│           │   ├── applier.py
│           │   ├── diff.py
│           │   └── safety.py
│           │
│           ├── model\         ← Document model / metadata runtime
│           │   ├── __init__.py
│           │   ├── document.py
│           │   ├── meta.py
│           │   ├── naming.py
│           │   ├── validation.py
│           │   ├── child_table.py
│           │   └── versioning.py
│           │
│           ├── permissions\   ← Role-based access control
│           │   ├── __init__.py
│           │   ├── engine.py
│           │   ├── roles.py
│           │   ├── user_permissions.py
│           │   └── cache.py
│           │
│           ├── printing\      ← Print formats + PDF
│           │   ├── __init__.py
│           │   ├── print_format.py
│           │   ├── renderer.py
│           │   └── pdf.py
│           │
│           ├── query_builder\ ← Dynamic query construction
│           │   ├── __init__.py
│           │   ├── filters.py
│           │   ├── compiler.py
│           │   ├── operators.py
│           │   └── dialects\
│           │       ├── __init__.py
│           │       ├── postgres.py
│           │       ├── sqlite.py
│           │       ├── mysql.py
│           │       └── mariadb.py
│           │
│           ├── realtime\      ← WebSocket / events
│           │   ├── __init__.py
│           │   ├── events.py
│           │   ├── pubsub.py
│           │   └── websocket.py
│           │
│           ├── reports\       ← Report engine
│           │   ├── __init__.py
│           │   ├── engine.py
│           │   ├── api.py
│           │   └── sql_guard.py
│           │
│           ├── scripts\       ← Server-side scripting
│           │   ├── __init__.py
│           │   ├── engine.py
│           │   ├── security.py
│           │   └── api.py
│           │
│           ├── search\        ← Global search index
│           │   ├── __init__.py
│           │   ├── index.py
│           │   └── query.py
│           │
│           ├── studio\        ← Galaxy Studio (DocType builder)
│           │   ├── __init__.py
│           │   ├── builder.py
│           │   ├── routes.py
│           │   ├── templates\
│           │   └── static\
│           │
│           ├── utils\         ← Shared utilities
│           │   ├── __init__.py
│           │   ├── dates.py
│           │   ├── json.py
│           │   ├── strings.py
│           │   ├── security.py
│           │   └── logging.py
│           │
│           ├── website\       ← Public website routes
│           │   ├── __init__.py
│           │   ├── routes.py
│           │   ├── renderer.py
│           │   └── templates\
│           │
│           ├── workflow\      ← Workflow engine
│           │   ├── __init__.py
│           │   ├── engine.py
│           │   ├── state.py
│           │   └── transition.py
│           │
│           └── www\           ← Public HTML pages
│               ├── index.html
│               ├── login.html
│               ├── setup.html
│               └── not_found.html
│
├── sites\                     ← Site configurations + data
│   ├── common_site_config.json
│   ├── platform.db
│   └── <site_name>\
│       ├── site_config.json
│       ├── logs\
│       └── backups\
│
├── public\                    ← Public web assets
│   ├── desk\
│   ├── studio\
│   ├── assets\
│   ├── icons\
│   └── images\
│
├── docs\                      ← Documentation
│   └── architecture\
│
├── tests\                     ← Test suite
│
├── logs\                      ← Server logs
├── config\                    ← Global config
│
├── pyproject.toml
├── README.md
├── AGENTS.md
└── STRUCTURE.md
```

## Migration Order (from current to target)

| Step | Source                          | Target                           | Status     |
|------|---------------------------------|----------------------------------|------------|
| 1    | internal/db/                    | galaxy/db/                       | ✓ Done     |
| 2    | internal/core/                  | galaxy/core/ (partial)           | ✓ Done     |
| 3    | galaxy/core/auth.py             | galaxy/auth/                     | ✓ Done     |
| 4    | galaxy/core/permissions.py      | galaxy/permissions/              | ✓ Done     |
| 5    | internal/http/server.py         | galaxy/ + galaxy/desk/routes.py  | Pending    |
| 6    | internal/http/templates/        | galaxy/desk/templates/           | Pending    |
| 7    | internal/http/static/           | galaxy/desk/static/              | Pending    |
| 8    | internal/config/                | galaxy/config.py                 | Pending    |
| 9    | internal/bootstrap/installer.py | galaxy/installer/                | Pending    |
| 10   | internal/cli/                   | galaxy/cli/                      | Pending    |
| 11   | internal/bench/                 | galaxy/bench_manager/            | Pending    |
| 12   | internal/site/                  | galaxy/ + galaxy/config.py       | Pending    |
| 13   | galaxy/core/crud.py             | galaxy/crud/                     | Pending    |
| 14   | galaxy/core/migration_*.py      | galaxy/migration/                | Pending    |
| 15   | galaxy/core/report_engine.py    | galaxy/reports/                  | Pending    |
| 16   | galaxy/core/script_engine.py    | galaxy/scripts/                  | Pending    |
| 17   | galaxy/core/security.py         | galaxy/utils/security.py         | Pending    |
| 18   | galaxy/core/tenant.py           | galaxy/auth/ (or core/)          | Pending    |
| 19   | galaxy/core/builder*.py         | galaxy/core/doctype/             | Pending    |
| 20   | galaxy/core/api.py              | galaxy/core/api.py (stays)       | Pending    |
| 21   | galaxy/core/repository.py       | galaxy/core/repository.py (stays)| Pending    |