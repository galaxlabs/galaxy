# App / Module / DocType Model

## Hierarchy

```
App (tabInstalled App)
 └── Module (tabInstalled Module + tabModule Def)
      └── DocType (tabDocType)
           ├── DocField (tabDocField) — field definitions
           ├── DocPerm (tabDocPerm) — permission rules
           ├── physical table "{tab}{DocType}" — data rows
           ├── Server Script — event hooks
           └── Report — query/script reports
```

## App

A Python package registered in a site. Currently only the `core` app exists.

Stored in `tabInstalled App`:
- `name` — primary key
- `app_name`, `app_version`, `enabled`

Installed via `install_app()` in `site_manager.py` — updates both `site_config.json` and `tabInstalled App`.

## Module

A logical grouping of DocTypes within an app. Current modules: Core, Setup, Security, Desk, Workspace, Navigation.

Stored in two tables:
- `tabInstalled Module` — which modules are enabled per app
- `tabModule Def` — module label, description, app association

A DocType belongs to exactly one module.

## DocType

The central metadata entity. Everything derives from DocType definitions.

Stored in `tabDocType`:
- `name` — document type name (e.g. "User", "Report")
- `module` — link to `tabModule Def`
- `app_name` — owning app
- `table_name` — physical table name (e.g. "tabUser", "tabReport")
- `is_single` — single-record DocType (no physical table; stored as JSON)
- `is_submittable` — has submit/amend lifecycle
- `is_child_table` — child table (no standalone CRUD)
- `is_tree` — tree structure with parent-child

### DocType ↔ Table Mapping

```
DocType "User"     → table "tabUser"
DocType "DocType"  → table "tabDocType"
DocType "Supplier" → table "tabSupplier"  (user-created)
```

Convention: table name = `tab` + DocType name (no spaces, no special chars).

## DocField

Fields of a DocType. The source of truth for column definitions, validation rules, and UI rendering.

Stored in `tabDocField`:
- `parent` — DocType this field belongs to
- `fieldname` — column name (snake_case)
- `label` — human-readable display label
- `fieldtype` — one of: Data, Int, Float, Currency, Check, Select, Text, Code, Link, JSON, Datetime, Date, Table
- `options` — type-specific configuration (Link target, Select options)
- `reqd`, `hidden`, `read_only`, `in_list_view` — boolean flags
- `idx` — sort order

## Metadata-Driven Flow

```
DocType + DocField → Migration Planner → CREATE TABLE SQL
DocType + DocField → CRUD Engine → Dynamic SELECT/INSERT/UPDATE/DELETE
DocType + DocField + DocPerm → Permission Check → Authorize/Deny
DocType + DocField → Desk UI → Auto-generated list + form
DocType + DocField + Script → Hook Execution → before_save, after_save, etc.
DocType + DocField + Report → Query/Report Execution
```

## Current Seeded DocTypes (13)

| DocType | Table | Fields |
|---------|-------|--------|
| Installed App | tabInstalled App | 6 |
| Installed Module | tabInstalled Module | 5 |
| Module Def | tabModule Def | 7 |
| DocType | tabDocType | 9 |
| DocField | tabDocField | 11 |
| DocPerm | tabDocPerm | 9 |
| User | tabUser | 6 + tenant_id |
| Role | tabRole | 3 |
| Has Role | tabHas Role | 4 + tenant_id |
| Error Log | tabError Log | 10 + tenant_id |
| Server Script | tabServer Script | 8 + tenant_id |
| Report | tabReport | 9 + tenant_id |
| Session | tabSession | 5 + tenant_id |

## Creating a New DocType

1. **Build payload** via DocType Builder (`/desk/builder/doctype/new`)
2. **Preview** → `plan_doctype_migration()` generates CREATE TABLE SQL
3. **Save** → `save_doctype_metadata()` writes to `tabDocType` + `tabDocField`
4. **Apply** → `apply_doctype_migration()` executes CREATE TABLE
5. **Use** → CRUD API + Desk UI available immediately