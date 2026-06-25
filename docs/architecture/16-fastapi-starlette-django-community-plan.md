# 16 — FastAPI / Starlette / Django Community Plan

## Why Galaxy Is Not a Django App

| Aspect             | Django                         | Galaxy                          |
|--------------------|--------------------------------|----------------------------------|
| **Source of truth**| Python models (models.py)      | DocType metadata (DB-driven)     |
| **Schema**         | Migrations from model changes  | Metadata-first, SQL generated    |
| **Admin**          | django.contrib.admin           | Galaxy Desk                      |
| **ORM**            | Django ORM                     | SQLAlchemy                       |
| **API**            | DRF / Ninja                    | Starlette / FastAPI              |
| **Settings**       | settings.py                    | site_config.json / env           |
| **CLI**            | manage.py                      | galaxy CLI                       |
| **App model**      | Django app (python package)    | Galaxy App (registered metadata) |

Galaxy is **not** a Django app because the data model is dynamic — DocTypes are created and modified at runtime through metadata, not through Python model classes. This metadata-driven architecture is the fundamental difference.

## How Django Developers Can Understand Galaxy

Galaxy mirrors Django's productivity goals but through different mechanisms:

| Concept                 | Django                          | Galaxy                              |
|-------------------------|----------------------------------|--------------------------------------|
| Project creation        | `django-admin startproject`      | `galaxy install`                     |
| App creation            | `manage.py startapp`             | `galaxy bench install-app`           |
| Data model              | `class Model(models.Model)`      | DocType metadata (JSON/DB)           |
| Fields                  | `CharField`, `IntegerField`, etc | DocField with fieldtype              |
| Admin UI                | django admin (register models)   | Galaxy Desk (auto-generated)         |
| Admin customization     | ModelAdmin class                 | DocType configuration                |
| Migrations              | `makemigrations` + `migrate`     | `galaxy migration preview/apply`     |
| Permissions             | `permissions` in Meta            | DocPerm + Role system                |
| Management commands     | `manage.py <command>`            | `galaxy <command>`                   |
| Settings                | `settings.py`                    | `sites/<site>/site_config.json`      |
| Templates               | Django templates                 | Jinja2 (same syntax)                 |
| URL routing             | `urls.py`                        | Starlette routes (or FastAPI router) |
| Database layer          | Django ORM                       | SQLAlchemy                           |

## pip Install Flow

```bash
pip install galaxy-framework

# Create a site + database
galaxy install

# Start development server
galaxy start

# Check installation
galaxy doctor
```

Optional Python module invocation:

```bash
python -m galaxy install
python -m galaxy start
```

## Settings/Config Similarities

Django developers expect a configuration file. Galaxy provides:

```json
# sites/common_site_config.json
{
    "developer_mode": true,
    "default_site": "local.dev",
    "allow_server_scripts": true,
    "csrf_enabled": true
}
```

```json
# sites/local.dev/site_config.json
{
    "db_type": "postgres",
    "db_host": "127.0.0.1",
    "db_port": 5432,
    "db_name": "galaxy_local",
    "db_user": "galaxy_user",
    "db_password": "..."
}
```

Environment variable override: `GALAXY_DB_NAME`, `GALAXY_DB_HOST`, etc.

## Why FastAPI vs Starlette

| Aspect               | Starlette                        | FastAPI                          |
|----------------------|----------------------------------|----------------------------------|
| **Layer**            | ASGI micro-framework             | Starlette + Pydantic + OpenAPI   |
| **OpenAPI docs**     | Manual integration               | Built-in (Swagger + ReDoc)       |
| **Validation**       | Manual (or integration)          | Pydantic (automatic)             |
| **Performance**      | Identical (FastAPI wraps it)     | Identical                        |
| **Dependencies**     | Minimal                          | More (pydantic, etc.)            |
| **Dynamic metadata** | No constraint (our validation)   | Pydantic may conflict with meta  |
| **Community**        | Smaller but focused              | Very large                       |
| **Best for Galaxy**  | **Recommended**                  | Optional for API consumers       |

**Decision:** Use Starlette as the core HTTP framework. It is lightweight, has no opinion on data validation (we do our own via DocField metadata), and is the foundation FastAPI itself builds on.

FastAPI can be offered as an **optional add-on** for API consumers who want OpenAPI docs. The core framework should not force Pydantic models on dynamic DocType data.

## Where SQLAlchemy Fits

SQLAlchemy is used for:

- **Engine/connection management:** `create_engine()`, connection pooling, session management.
- **Dialect abstraction:** automatic quoting, type mapping, DDL generation.
- **Textual SQL:** `sqlalchemy.text()` for parameterized queries.
- **Core API:** `insert()`, `update()`, `delete()`, `select()` for dynamic table operations.
- **Migration DDL:** `ALTER TABLE`, `CREATE TABLE`, `DROP TABLE` per dialect.

SQLAlchemy ORM (declarative models) is **not used** for application DocTypes because DocTypes are dynamic — not defined as Python classes. ORM is used only for fixed internal tables (platform DB, session store, etc.).

## Where DocType Metadata Remains Source of Truth

```
User creates/edits DocType → metadata saved in tabDocType/tabDocField
Migration preview generates SQL from metadata
Migration apply executes SQL
CRUD reads metadata to build dynamic queries
Desk reads metadata to build dynamic forms/lists
```

Python code never hardcodes application table schemas. The metadata layer is the single source of truth.