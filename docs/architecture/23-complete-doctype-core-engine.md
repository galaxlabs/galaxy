# Complete DocType Core Engine

## 1. Purpose

This document defines the complete architecture for the Galaxy Framework DocType core engine. The engine treats **metadata as the sole source of truth** — every aspect of a DocType's behavior (database structure, form rendering, validation, permissions, scripting, customization) flows from layered metadata that is merged at runtime into a single `RuntimeMeta` object.

The design avoids monolithic DocType tables. Instead, concerns are separated into specialized metadata objects, each responsible for one dimension of behavior. This enables clean extensibility without modifying base metadata.

## 2. Core DocType Philosophy

```
Metadata is the source of truth.
```

Every design decision follows from this principle:

- **Database tables** are derived from DocType + DocField metadata, never hand-written.
- **Form rendering** is derived from field metadata, never hardcoded.
- **Validation** is derived from field rules, never embedded in controllers.
- **Permissions** are derived from layered rule objects, never scattered across code.
- **Customization** is additive — custom fields and property setters overlay base metadata at runtime.
- **No code generation** for the core engine — metadata drives behavior directly. Code generation is reserved for integrations, SDKs, and stubs.

## 3. Core Metadata Objects

```
DocType                 — table definition, settings, controller reference
DocField                — column definition, validation, display properties
DocPerm                 — role-level CRUD permissions
CustomField             — user-added fields (separate from base fields)
PropertySetter          — targeted overrides on any metadata property
DocTypeOverride         — controller/service/validation replacement
DocTypeSetting          — per-DocType operational settings
FieldRule               — field-level validation logic
FieldDependency         — field visibility/behavior based on other fields
ComputedField           — field whose value comes from an expression
ValidationRule          — document-level validation rules
DisplayLogic            — field visibility conditions (evaluated client-side)
ClientScript            — browser-side behavior per DocType
ServerScript            — server-side hooks (before_insert, validate, etc.)
DocTypeAction           — custom actions available in the UI
DocTypeProcess          — multi-step processes associated with a DocType
DocTypeWebView          — public/guest view configuration
DocTypeIntegration      — webhook, API, or export configuration
DocTypeVersion          — change history record
Comment                 — user and system comments on documents
Mention                 — @mention records with notification state
NotificationRule        — when and how to notify about document events
PermissionRule          — multi-dimensional permission conditions
FieldPermission         — field-level read/write access rules
DataMaskRule            — field-level privacy masking
DynamicFieldSource      — runtime field option sources (query, API, etc.)
CodeGenerationBlock     — template for generating SDKs, tests, stubs
```

## 4. Dynamic Property Loading

Properties are resolved at runtime through a layered merge pipeline. No single metadata object holds all properties — each layer contributes and overrides.

### Property Resolution Layers

```
1. Base DocType metadata (source of truth for structure)
2. DocField definitions (column-level metadata)
3. DocType settings (operational flags)
4. Custom fields (user-added fields, merged into field list)
5. Property setters (targeted property overrides)
6. DocType overrides (behavioral replacement)
7. Permission filters (field-level access trimming)
8. Contextual rules (role/user/tenant conditions)
```

### Resolution Priority

```
Lowest:  Base metadata
         Custom fields (added to field list)
         Property setters (override individual properties)
         DocType overrides (replace behavior)
Highest: Permission filters (deny-first, removed from output)
```

### Property Setter Resolution Order

When multiple property setters target the same property, they are applied in priority order:

1. Sort by `priority` (higher = applied last, wins)
2. Sort by specificity (site-specific > role-specific > user-specific > global)
3. Last write wins within same priority

## 5. Property Setter System

Property Setters allow targeted overrides of any metadata property without modifying the base definition. They are the primary mechanism for customization.

### Property Setter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `target_type` | Select | DocType / DocField / Action / View / Permission |
| `target_name` | Data | Name of the specific target (field name, action name, etc.) |
| `property_name` | Data | The property to override (e.g. `reqd`, `hidden`, `label`) |
| `property_value` | Text | The new value (parsed per `property_type`) |
| `property_type` | Select | Data type of the value: Int / Float / Check / Data / Text / JSON |
| `applies_to_site` | Link | Optional — restrict to a specific site |
| `applies_to_role` | Link | Optional — restrict to a specific role |
| `applies_to_user` | Link | Optional — restrict to a specific user |
| `condition` | Code | Optional — expression evaluated to determine applicability |
| `enabled` | Check | Whether this setter is active |
| `priority` | Int | Resolution priority (0–1000, higher wins) |
| `source_app` | Data | Which app installed this setter |
| `created_by` | Data | Who created it |
| `created_at` | Datetime | When it was created |

### Examples

```
Target DocType: ToDo
Target type: DocField
Target name: description
Property name: reqd
Property value: true
Property type: Check
→ Makes the description field required

Target DocType: Customer
Target type: DocField
Target name: phone
Property name: hidden
Property value: true
Property type: Check
→ Hides the phone field

Target DocType: Sales Invoice
Target type: DocField
Target name: due_date
Property name: label
Property value: "Payment Due By"
Property type: Data
→ Changes the field label
```

## 6. Custom Field System

Custom Fields allow users to add new fields to existing DocTypes without modifying the base schema. They are stored separately and merged at runtime.

### Custom Field Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `fieldname` | Data | Field name (auto-generated from label if empty) |
| `label` | Data | Display label |
| `fieldtype` | Select | Field type from the field dictionary |
| `options` | Text / JSON | Type-specific options (e.g. target DocType for Link) |
| `insert_after` | Data | Insert this field after the specified fieldname |
| `reqd` | Check | Required field |
| `read_only` | Check | Read-only field |
| `hidden` | Check | Hidden field |
| `in_list_view` | Check | Show in list view |
| `in_filter` | Check | Show in filter area |
| `default` | Data | Default value |
| `description` | Text | Help text |
| `validation_rule` | Link | Optional — associated Field Rule |
| `display_logic` | Link | Optional — associated Display Logic |
| `permission_rule` | Link | Optional — associated Field Permission |
| `source_app` | Data | Which app created this custom field |
| `enabled` | Check | Whether the field is active |

### Merge Rules

- Custom fields are appended to the base DocField list.
- Field ordering is determined by `insert_after` — if empty, appended at the end.
- Custom fields can reference the same field dictionaries as base fields (validation, display logic, permissions).
- If a custom field's `fieldname` matches a base field, the custom field overrides the base field entirely.
- Custom fields are NOT written into base DocField tables — they remain in the Custom Field table exclusively.

## 7. Customization Rules

Customization rules govern how metadata can be modified at runtime:

| Rule | Description |
|------|-------------|
| Custom fields never modify base DocField rows | They exist in their own table and merge at runtime |
| Property setters never modify base rows | They are applied on top during the merge |
| Overrides replace behavior | They are referenced by the runtime but stored in their own table |
| Deletions are soft | Disable via `enabled=false` rather than deleting rows |
| App installs can create custom fields | Apps define custom fields in their hooks, applied during install |
| Customization is traceable | Every customization has a `source_app` and `created_by` |

## 8. Override Rules

DocType Override allows app-level or site-level replacement of core behavior without modifying base code.

### DocType Override Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `override_type` | Select | controller / service / validation / naming / permission / view / action |
| `handler` | Code | The replacement implementation (Python path or inline code) |
| `priority` | Int | Resolution priority (higher wins) |
| `condition` | Code | Expression — only apply if condition is met |
| `enabled` | Check | Whether this override is active |
| `source_app` | Data | Which app defines this override |

### Override Targets

| Type | What It Replaces |
|------|------------------|
| `controller` | The DocType controller class (full replacement) |
| `service` | A specific service method (e.g. `validate`, `on_update`) |
| `validation` | Validation logic for specific conditions |
| `naming` | The naming series strategy |
| `permission` | Permission evaluation strategy (e.g. always deny for certain roles) |
| `view` | Custom view rendering logic |
| `action` | Custom action handler |

### Resolution

```
1. Load base controller/service/validation
2. Check for overrides by override_type + doctype
3. If override exists and enabled and condition matches:
   - Use override handler instead of base
4. If multiple overrides match:
   - Sort by priority (descending)
   - Apply highest priority override
```

## 9. DocType Settings

Per-DocType settings control operational behavior. These are stored as a single row per DocType in the DocType Setting table, with sensible defaults.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `allow_create` | Check | true | Allow creating new documents |
| `allow_update` | Check | true | Allow updating existing documents |
| `allow_delete` | Check | true | Allow deleting documents |
| `allow_import` | Check | true | Allow CSV/JSON import |
| `allow_export` | Check | true | Allow CSV/JSON export |
| `allow_comments` | Check | true | Allow comments on documents |
| `allow_mentions` | Check | true | Allow @mentions |
| `allow_attachments` | Check | true | Allow file attachments |
| `allow_versions` | Check | true | Track version history |
| `allow_web_view` | Check | false | Enable public web view |
| `allow_public_api` | Check | false | Enable public REST API access |
| `track_changes` | Check | true | Record field-level changes |
| `track_seen` | Check | false | Record when users view documents |
| `search_enabled` | Check | true | Include in global search |
| `audit_level` | Select | `basic` | Audit detail level: `none` / `basic` / `full` |
| `max_file_size` | Int | 10485760 | Max attachment size in bytes |
| `default_list_view` | Select | `list` | Default view: `list` / `report` / `kanban` |
| `default_sort_field` | Data | `modified` | Default sort column |
| `default_sort_order` | Select | `desc` | `asc` / `desc` |

Settings can be overridden by Property Setters with target_type `DocType` and target_name `_settings`.

### DocType Exposure Targeting

Each DocType can target one or more user worlds for access. Exposure is controlled by:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `exposure` | Select | `system` | Which world the DocType is exposed to: `system`, `portal`, `public`, `all` |
| `portal_permission_model` | Select | `none` | Portal permission model: `none`, `owner`, `profile_link`, `shared`, `public` |
| `allow_portal_view` | Check | false | Enable portal list/form views |
| `allow_portal_create` | Check | false | Allow portal users to create records |
| `allow_portal_update` | Check | false | Allow portal users to update records |
| `allow_portal_delete` | Check | false | Allow portal users to delete records |
| `allow_web_view` | Check | false | Enable public read access |
| `allow_public_api` | Check | false | Enable public REST API access |

- **`exposure = system`** — DocType only accessible via Desk and internal API. No portal or public access.
- **`exposure = portal`** — DocType accessible via portal routes and portal API, in addition to system.
- **`exposure = public`** — DocType accessible to guests via public routes (read-only unless public forms are configured).
- **`exposure = all`** — DocType accessible across all three worlds with appropriate restrictions per world.

Each exposure level uses its own permission/view layer:
- System access → evaluated through DocPerm + FieldPermission + PermissionRule (see Doc 28 §3.4)
- Portal access → evaluated through PortalPermission + PortalFieldPermission + PortalProfileLink (see Doc 28 §4.4)
- Public access → evaluated through PublicViewRule + PublicForm + PublicAccessToken (see Doc 28 §5.4)

## 10. Field Type Dictionary Extension

Extend the base field type dictionary with support for industry-wide types. Each field type defines its behavior across multiple dimensions.

### Complete Field Type Enumeration

| # | Field Type | Database Column | Python Type | Form Renderer | List Renderer | Filter | Search | Mask Support |
|---|-----------|-----------------|-------------|---------------|---------------|--------|--------|--------------|
| 1 | Data | `VARCHAR(255)` | str | `<input type="text">` | Text, truncate 100 | `ILIKE` | `ILIKE` | Yes |
| 2 | Small Text | `VARCHAR(1024)` | str | `<textarea rows=3>` | Text, truncate 80 | `ILIKE` | `ILIKE` | Yes |
| 3 | Long Text | `TEXT` | str | `<textarea rows=8>` | Truncate 120 + expand | None | `ILIKE` | Yes |
| 4 | Int | `INTEGER` | int | `<input type="number" step=1>` | Right-aligned number | `=` `>` `<` `>=` `<=` `!=` | `=` | No |
| 5 | Float | `DOUBLE PRECISION` | float | `<input type="number" step=any>` | Right-aligned, 2 decimals | `=` `>` `<` `>=` `<=` `!=` | `=` | No |
| 6 | Currency | `DOUBLE PRECISION` | float | `<input type="number" step=any>` | Formatted with currency symbol | Range | `=` | No |
| 7 | Percent | `DOUBLE PRECISION` | float | `<input type="number" step=0.01>` | Appended `%` sign | Range | `=` | No |
| 8 | Check | `BOOLEAN` | bool | `<input type="checkbox">` | Checkmark or cross | `=` | `=` | No |
| 9 | Date | `DATE` | date | `<input type="date">` | Formatted date | Range | `=` | No |
| 10 | Time | `TIME` | time | `<input type="time">` | Formatted time | Range | `=` | No |
| 11 | Datetime | `TIMESTAMP` | datetime | `<input type="datetime-local">` | Formatted datetime | Range | `=` | No |
| 12 | Duration | `INTEGER` | int (seconds) | `<input type="text">` with format | `Xh Ym` | Range | `=` | No |
| 13 | Select | `VARCHAR(255)` | str | `<select>` with options | Option label | `=` | `=` | No |
| 14 | Multi Select | `TEXT` (JSON array) | list[str] | Tag-style selector | Tags | `@>` JSON contains | `ILIKE` | No |
| 15 | Link | `VARCHAR(255)` | str | Searchable link selector | Hyperlinked value | `=` | `ILIKE` | Yes |
| 16 | Dynamic Link | `VARCHAR(255)` | str | Searchable, field-driven doctype | Hyperlinked value | `=` | `ILIKE` | Yes |
| 17 | Table | (child table) | list[dict] | Inline editable grid | Row count badge | None | None | No |
| 18 | Table MultiSelect | (child table) | list[dict] | Tag grid | Tags | None | None | No |
| 19 | Attach | `VARCHAR(512)` | str (file URL) | File uploader | Download link | None | `ILIKE` | No |
| 20 | Attach Image | `VARCHAR(512)` | str (file URL) | Image upload + preview | Thumbnail | None | `ILIKE` | No |
| 21 | Image | `VARCHAR(512)` | str (URL) | Image URL input | Thumbnail | None | `ILIKE` | No |
| 22 | JSON | `JSONB` / `TEXT` | dict / list | Code editor (JSON) | JSON preview | `@>` | `ILIKE` | No |
| 23 | Code | `TEXT` | str | Code editor (syntax highlighting) | Truncated | None | None | No |
| 24 | HTML | `TEXT` | str (HTML) | Rich text or code editor | Rendered HTML snippet | None | None | No |
| 25 | Markdown | `TEXT` | str | Markdown editor with preview | Rendered Markdown | None | None | No |
| 26 | Color | `VARCHAR(7)` | str (hex) | Color picker | Color swatch | `=` | `=` | No |
| 27 | Rating | `INTEGER` (1–5) | int | Star rating widget | Star display | `>=` | `=` | No |
| 28 | Barcode | `VARCHAR(255)` | str | Barcode input | Barcode image | `ILIKE` | `ILIKE` | No |
| 29 | QR Code | `VARCHAR(512)` | str | QR input | QR image | `ILIKE` | `ILIKE` | No |
| 30 | Geolocation | `JSONB` (lat/lng) | dict[str, float] | Map picker | Map link | None | None | No |
| 31 | Signature | `TEXT` (SVG/PNG) | str | Signature pad | Signature image | None | None | No |
| 32 | Password | `VARCHAR(255)` | str | `<input type="password">` | Masked `••••••` | None | None | No |
| 33 | Phone | `VARCHAR(50)` | str | `<input type="tel">` | Formatted | `ILIKE` | `ILIKE` | Yes |
| 34 | Email | `VARCHAR(255)` | str | `<input type="email">` | Mailto link | `ILIKE` | `ILIKE` | Yes |
| 35 | URL | `VARCHAR(1024)` | str | `<input type="url">` | Hyperlink | `ILIKE` | `ILIKE` | No |
| 36 | Read Only | (depends on type) | (depends) | Text display only | Text display | None | None | No |
| 37 | Section Break | `—` (no column) | — | Visual section divider | — | — | — | — |
| 38 | Column Break | `—` (no column) | — | Visual column divider | — | — | — | — |
| 39 | Tab Break | `—` (no column) | — | Visual tab divider | — | — | — | — |
| 40 | Button | `—` (no column) | — | Clickable button | — | — | — | — |
| 41 | Web View | `—` (no column) | — | Embedded web view | — | — | — | — |
| 42 | Formula | (depends on output) | (depends) | Read-only evaluated value | Evaluated value | None | None | No |
| 43 | Computed | (depends on output) | (depends) | Read-only computed value | Computed value | None | None | No |
| 44 | Hidden | (depends on type) | (depends) | Not rendered | Not rendered | None | None | No |

### Field Type Dimensions

For each field type, the engine maintains:

- **Database type**: The SQL column type for CREATE TABLE / ALTER TABLE.
- **Validation**: Python-level validation applied before save.
- **Form renderer**: HTML template or component used for editing.
- **List renderer**: HTML template or component used for list display.
- **Filter behavior**: Allowed filter operators.
- **Search behavior**: How this field participates in global search.
- **Import/export behavior**: CSV/JSON serialization rules.
- **Permission behavior**: Whether field-level permissions apply.
- **Mask/privacy support**: Whether the field can be masked for privacy.
- **Migration risk**: Risk level for schema changes (safe / rename only / destructive).

## 11. Field Validation Rules

Validation Rules define document-level and field-level constraints. They are stored as separate metadata objects evaluated at runtime.

### Field Rule Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `fieldname` | Data | Target field (or empty for document-level) |
| `rule_type` | Select | `min_value` / `max_value` / `min_length` / `max_length` / `pattern` / `custom_function` / `unique` / `existing` |
| `rule_value` | Data | The constraint value (number, pattern string, function path) |
| `error_message` | Text | User-facing error message |
| `condition` | Code | Optional — only apply when this expression is true |
| `priority` | Int | Evaluation priority |
| `enabled` | Check | Whether this rule is active |
| `source_app` | Data | Which app defined this rule |

### Built-In Validation Rules

| Rule Type | Description |
|-----------|-------------|
| `min_value` | Numeric minimum (Int, Float, Currency, Percent) |
| `max_value` | Numeric maximum (Int, Float, Currency, Percent) |
| `min_length` | Minimum string length (Data, Small Text, Phone, Email, URL) |
| `max_length` | Maximum string length (Data, Small Text, Phone, Email, URL) |
| `pattern` | Regular expression match (any text field) |
| `unique` | Value must be unique across all documents of this DocType |
| `existing` | If Link, verify the referenced document exists |
| `custom_function` | Call a Python function that returns True/False + message |

### Evaluation

```
1. Gather all Field Rules for the DocType
2. Filter by fieldname (if set)
3. Filter by enabled=true
4. Sort by priority
5. For each rule:
   a. If condition is set, evaluate it
   b. If condition passes, apply the rule
   c. If rule fails, collect the error message
6. If any errors, reject the save with all error messages
```

## 12. Field Dependency Rules

Field Dependencies control when fields are shown, hidden, required, or read-only based on the values of other fields.

### Field Dependency Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `fieldname` | Data | The field whose behavior is controlled |
| `depends_on_field` | Data | The field whose value is checked |
| `operator` | Select | `=` / `!=` / `in` / `not in` / `>` / `<` / `>=` / `<=` / `is_set` / `is_not_set` |
| `value` | Data | The value to compare against |
| `action` | Select | `show` / `hide` / `require` / `readonly` / `filter_options` / `set_default` |
| `condition_group` | Data | Logical group for AND/OR grouping |
| `priority` | Int | Evaluation priority |
| `enabled` | Check | Whether this dependency is active |

### Multiple Conditions

Dependencies can be grouped:

- Within the same `condition_group`, all conditions are AND-ed.
- Different groups are OR-ed.
- Nested groups (using JSON) allow arbitrary boolean logic.

### Example

```
Show tax_id only when customer_type = "Company":
  doctype: Customer
  fieldname: tax_id
  depends_on_field: customer_type
  operator: =
  value: "Company"
  action: show
```

## 13. Mathematical / Computed Field Rules

Computed Fields derive their value from an expression evaluated against other fields in the document.

### Computed Field Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `fieldname` | Data | The computed field to store the result |
| `expression` | Code | The expression to evaluate |
| `dependencies` | JSON | List of fieldnames this expression depends on |
| `compute_on` | Select | `client` / `server` / `both` |
| `store_value` | Check | Whether to persist the computed value to the database |
| `precision` | Int | Decimal precision for numeric results |
| `rounding` | Select | `round` / `ceil` / `floor` / `truncate` |
| `condition` | Code | Optional — only compute when this condition is true |
| `enabled` | Check | Whether this computed field is active |

### Examples

```
amount = qty * rate
  fieldname: amount
  expression: doc.qty * doc.rate
  dependencies: ["qty", "rate"]
  compute_on: both
  store_value: true

total = subtotal + tax
  fieldname: total
  expression: doc.subtotal + doc.tax
  dependencies: ["subtotal", "tax"]
  compute_on: server
  store_value: true

age = today - date_of_birth (years)
  fieldname: age
  expression: (date.today() - doc.date_of_birth).days // 365
  dependencies: ["date_of_birth"]
  compute_on: both
  store_value: false
```

### Security

- Expressions must not execute arbitrary Python.
- Use a safe expression parser (e.g. a restricted eval with whitelisted functions and operators).
- Whitelisted functions: `round`, `ceil`, `floor`, `abs`, `min`, `max`, `sum`, `len`, `str`, `int`, `float`, `bool`, `date`, `datetime`, `timedelta`, `now`, `today`, `concat`, `if`, `coalesce`.
- Access to `doc.*` fields is permitted.
- Access to `doc.meta.*` is read-only.
- No imports, no attribute access beyond `doc.*`, no method calls on arbitrary objects.

## 14. Dynamic Field Loading

Some fields need their options populated at runtime from a dynamic source — a database query, an API call, or a script.

### Dynamic Field Source Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `fieldname` | Data | The field whose options are dynamically loaded |
| `source_type` | Select | `static` / `query` / `api` / `script` / `integration` |
| `source_handler` | Code | The handler for dynamic loading (SQL, API path, script path) |
| `filters` | JSON | Optional — mapping of field values to filter parameters |
| `depends_on` | JSON | Optional — list of fields whose values trigger reload |
| `cache_ttl` | Int | Cache time-to-live in seconds (0 = no cache) |
| `permission_required` | Link | Optional — role required to see this source |
| `enabled` | Check | Whether this dynamic source is active |

### Source Types

| Type | Behavior |
|------|----------|
| `static` | Options come from the field's `options` property directly (default) |
| `query` | Options come from a SQL query (must be SELECT, whitelisted) |
| `api` | Options come from an API call to a registered endpoint |
| `script` | Options come from a registered Server Script |
| `integration` | Options come from an external system via DocType Integration |

### Examples

```
Load cities based on selected country:
  source_type: query
  source_handler: SELECT name FROM tabCity WHERE country = %(country)s
  filters: {"country": "country"}
  depends_on: ["country"]

Load contacts based on selected customer:
  source_type: query
  source_handler: SELECT name FROM tabContact WHERE customer = %(customer)s
  filters: {"customer": "customer"}
  depends_on: ["customer"]
```

### Caching

- Cache results in the RuntimeMeta cache.
- Invalidate when source data changes or cache_ttl expires.
- Cache key: `doctype + fieldname + serialize(filters)`.

## 15. Dynamic DocType Loading

The runtime exposes an internal API for loading and caching DocType metadata.

### Internal API

| Function | Description |
|----------|-------------|
| `get_meta(doctype)` | Load base DocType + DocFields from the database |
| `get_field(doctype, fieldname)` | Load a single field with all overrides applied |
| `get_runtime_meta(doctype, user=None)` | Load full RuntimeMeta for a doctype with all layers merged |
| `clear_meta_cache(doctype)` | Clear the cached RuntimeMeta for a specific doctype |
| `reload_doctype(doctype)` | Clear cache and force reload on next access |

### Merge Flow

```
get_runtime_meta(doctype, user):
  1. Check cache → if hit and not stale, return cached RuntimeMeta
  2. Load base DocType metadata (table schema, settings, fields)
  3. Load Custom Fields for this DocType → merge into field list
  4. Load Property Setters for this DocType → apply to matching targets
  5. Load DocType Overrides → register behavioral replacements
  6. Load DocType Settings → apply operational flags
  7. Load Field Rules, Dependencies, Display Logic → attach to fields
  8. Load Client Scripts, Server Scripts, Actions → register
  9. Load Field Permissions, Mask Rules → attach to fields
  10. If user provided:
      a. Load user's roles
      b. Filter fields by Field Permissions
      c. Apply Data Mask Rules
      d. Filter Actions by user permissions
  11. Build RuntimeMeta object
  12. Cache and return
```

### RuntimeMeta Object Structure

```
RuntimeMeta:
  doctype_name: str
  table_name: str
  fields: list[RuntimeField]
  settings: DocTypeSetting
  overrides: list[DocTypeOverride]
  rules: list[FieldRule | ValidationRule]
  dependencies: list[FieldDependency]
  computed_fields: list[ComputedField]
  display_logic: list[DisplayLogic]
  client_scripts: list[ClientScript]
  server_scripts: list[ServerScript]
  actions: list[DocTypeAction]
  processes: list[DocTypeProcess]
  web_view: DocTypeWebView | None
  integrations: list[DocTypeIntegration]
  field_permissions: dict[str, list[FieldPermission]]
  mask_rules: dict[str, list[DataMaskRule]]
  dynamic_sources: dict[str, DynamicFieldSource]
```

## 16. Field-Level Permissions

Field-level permissions control which fields a user can read, write, export, or search.

### Field Permission Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `fieldname` | Data | Target field |
| `role` | Link | Optional — restrict to a specific role |
| `user` | Link | Optional — restrict to a specific user |
| `condition` | Code | Optional — expression for contextual matching |
| `can_read` | Check | Allow reading this field |
| `can_write` | Check | Allow writing this field |
| `can_export` | Check | Allow exporting this field |
| `can_import` | Check | Allow importing this field |
| `can_print` | Check | Allow printing this field |
| `can_search` | Check | Allow searching this field |
| `mask_rule` | Link | Optional — associated Data Mask Rule |
| `priority` | Int | Resolution priority |
| `enabled` | Check | Whether this rule is active |

### Permission Resolution

```
1. Start from the DocType-level permission (DocPerm).
2. If DocType denies access → field permissions are not evaluated.
3. If DocType allows access → check field-level permissions.
4. If no field-level permission exists for a field → inherited from DocType.
5. If field-level permission exists:
   - Deny on any access type (can_read=false) wins over allow
   - If multiple field permissions match (by role/user):
     - Most specific match wins (user > role > global)
     - Deny wins over allow at the same specificity
6. System Manager bypass can be configured to skip field-level checks.
```

## 17. Multi-Dimensional Permissions

Expand permissions beyond role-level DocPerm to support multiple dimensions.

### Permission Dimensions

| Dimension | Description |
|-----------|-------------|
| `role` | Standard role-based access |
| `user` | Per-user access grants |
| `owner` | Document owner has special access |
| `company` | Multi-company isolation |
| `branch` | Branch-level access |
| `department` | Department-level access |
| `region` | Geographic region access |
| `team` | Team-based access |
| `record_status` | Access based on docstatus or workflow state |
| `custom_condition` | Arbitrary Python condition |
| `tenant` | Multi-tenant isolation |
| `time_window` | Access allowed only during certain hours |

### Permission Rule Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `role` | Link | Optional — target role |
| `permission_type` | Select | `read` / `write` / `create` / `delete` / `submit` / `cancel` / `amend` / `export` / `import` / `print` / `email` / `share` / `comment` / `mention` / `attach` / `run_action` / `run_report` |
| `condition` | Code | Expression evaluated against the document context |
| `dimension_type` | Select | Which dimension this rule applies to |
| `dimension_value` | Data | The specific value for the dimension |
| `applies_to_field` | Data | Optional — field whose value is checked against dimension_value |
| `applies_to_action` | Select | Optional — restrict to a specific action |
| `priority` | Int | Resolution priority |
| `enabled` | Check | Whether this rule is active |

### Permission Types

| Type | Controls |
|------|----------|
| `read` | List and view documents |
| `write` | Update existing documents |
| `create` | Create new documents |
| `delete` | Delete documents |
| `submit` | Submit (change docstatus to 1) |
| `cancel` | Cancel (change docstatus to 2) |
| `amend` | Create amended copy |
| `export` | Export to CSV/JSON |
| `import` | Import from CSV/JSON |
| `print` | Print document |
| `email` | Email document |
| `share` | Share document with other users |
| `comment` | Add comments |
| `mention` | Mention other users |
| `attach` | Attach files |
| `run_action` | Execute custom actions |
| `run_report` | Run reports on this DocType |

### Evaluation

```
1. DocType-level permission check (DocPerm) runs first.
2. If DocType allows → evaluate Permission Rules.
3. Collect all Permission Rules for (doctype, permission_type, enabled).
4. For each matching rule:
   a. Check dimension (role, user, owner, etc.)
   b. Evaluate condition expression
   c. If condition passes → apply rule
5. If any rule denies → deny.
6. If any rule allows → allow.
7. If no rule matches → use the DocPerm default.
```

## 18. Masking and Privacy Rules

Data masking protects sensitive field values by hiding them from unauthorized viewers.

### Data Mask Rule Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `fieldname` | Data | Target field |
| `mask_type` | Select | `full` / `partial` / `email` / `phone` / `custom` |
| `visible_to_roles` | JSON | List of roles that can see the unmasked value |
| `visible_to_users` | JSON | List of users that can see the unmasked value |
| `condition` | Code | Optional — only apply masking when this condition is true |
| `audit_on_reveal` | Check | Log an audit event when a user views the unmasked value |
| `enabled` | Check | Whether this mask rule is active |

### Mask Types

| Type | Display | Example |
|------|---------|---------|
| `full` | Full hide (show `***`) | `********` |
| `partial` | Show first/last characters | `A*****son` or `*****smith` |
| `email` | Mask email prefix, keep domain | `a***@domain.com` |
| `phone` | Mask middle digits | `0300****818` |
| `custom` | Custom regex-based masking | Configurable pattern |

### Privacy Overlays

- Fields with mask rules are rendered with masked values in both form and list views.
- A "Reveal" action can be used to temporarily show the unmasked value.
- Revealing generates an audit event if `audit_on_reveal` is true.
- Export always uses masked values for masked fields unless the exporter has explicit unmask permission.

## 19. Web View / Public View

DocType Web View enables public or guest access to documents for portals, share links, and public pages.

### DocType Web View Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `enabled` | Check | Enable web view for this DocType |
| `route_pattern` | Data | URL pattern (e.g. `/docs/<name>`, `/public/<slug>`) |
| `title_field` | Data | Field to use as the page title |
| `image_field` | Data | Field to use as the page image (OG meta) |
| `public_fields` | JSON | List of fields visible to guests |
| `template` | Code | Optional — custom Jinja2 template path |
| `allow_guest` | Check | Allow unauthenticated access |
| `require_token` | Check | Require a share token in the URL |
| `seo_title` | Data | SEO meta title |
| `seo_description` | Text | SEO meta description |
| `cache_ttl` | Int | Cache TTL in seconds |
| `permission_rule` | Link | Optional — Field Rule for guest access granularity |

### Use Cases

- Public job postings from a Job DocType.
- Order status pages for customers (token-based).
- Public knowledge base articles.
- Self-service portal pages.

## 20. Client Script Model

Client Scripts define browser-side behavior for DocType forms, lists, and views.

### Client Script Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `script_type` | Select | `form` / `list` / `view` / `report` |
| `script` | Code | JavaScript code |
| `enabled` | Check | Whether this script is active |
| `priority` | Int | Load priority |
| `allowed_roles` | JSON | Optional — restrict execution to these roles |
| `version` | Int | Script version (incremented on change) |
| `audit_required` | Check | Audit all actions triggered by this script |

### Client API

```javascript
// Form events
galaxy.form.on("Customer", {
  refresh(form) {
    form.addButton("Verify", async () => {
      await form.call("verify_customer");
    });
  },

  customer_type(form) {
    form.toggle("tax_id", form.value("customer_type") === "Company");
  }
});

// List events
galaxy.list.on("Customer", {
  refresh(list) {
    list.addAction("Export Selected", async (items) => {
      await list.export(items);
    });
  }
});

// Field event naming
galaxy.form.on("Customer", {
  // Fieldname as event name fires when field value changes
  customer_type(form) { ... },
  email(form) { ... }
});
```

### Security Rules

- Client scripts cannot bypass server-side permissions.
- Client scripts can only call whitelisted server actions (registered via `galaxy.whitelist`).
- Script errors are caught and logged to Error Log.
- Script execution does not block form rendering (async loading).
- Each script is versioned — stale cached scripts are re-fetched.

## 21. Server Script Generation Model

Server Scripts define server-side hooks that execute during document lifecycle events.

### Server Script Types

| Type | When It Executes |
|------|------------------|
| `before_insert` | Before a new document is saved |
| `after_insert` | After a new document is saved |
| `before_update` | Before an existing document is updated |
| `after_update` | After an existing document is saved |
| `before_delete` | Before a document is deleted |
| `validate` | During validation phase (can reject save) |
| `on_submit` | When a document is submitted |
| `on_cancel` | When a document is cancelled |
| `scheduled` | Runs on a schedule (cron-like) |
| `api` | Custom API endpoint handler |
| `action` | Custom action handler |

### Script Generation

The Galaxy Builder can generate safe Server Script templates from configured actions and rules:

```python
# Generated before_insert script for Customer
def before_insert(doc, method):
    """
    Auto-generated: Set default customer group
    """
    if not doc.customer_group:
        doc.customer_group = "Individual"

# Generated validate script for Sales Invoice
def validate(doc, method):
    """
    Auto-generated: Prevent negative totals
    """
    if doc.total < 0:
        frappe.throw("Total cannot be negative")
```

### Security Rules

- Generated scripts are **disabled by default** until reviewed.
- Dangerous imports are blocked (same blocked module list as Report Engine).
- Raw SQL is blocked unless explicitly allowed in the DocType Setting.
- All script errors are logged to Error Log.
- Script execution has a timeout (configurable, default 30 seconds).
- An audit trail is required for all script changes.
- Scripts that modify documents outside their doctype must be explicitly permitted.

## 22. Code Generation Blocks

Code Generation Blocks define templates for generating SDKs, integration stubs, tests, and other derived code.

### Code Generation Block Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType (or empty for framework-level blocks) |
| `block_type` | Select | `api` / `service` / `validation` / `client_script` / `server_script` / `integration` / `test` / `ui_component` |
| `template` | Code | Jinja2 template for the generated output |
| `output_path` | Data | Relative path for generated files |
| `language` | Select | Target language: `python` / `javascript` / `typescript` / `go` / `yaml` |
| `enabled` | Check | Whether this block is active |
| `generated_hash` | Data | Hash of last generated output (for change detection) |
| `last_generated_at` | Datetime | When this block was last generated |

### Use Cases

- **SDK generation**: Generate typed Python/TS clients from DocType metadata.
- **Test generation**: Generate test skeletons for CRUD operations.
- **Action handler generation**: Generate server script stubs from Action metadata.
- **Integration stub generation**: Generate webhook receivers or API callers.
- **UI component generation**: Generate form/list component code for external UIs.

## 23. Actions and Processes

Actions are user-triggered operations on a document. Processes are multi-step workflows associated with a DocType.

### DocType Action Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `label` | Data | Button label shown to users |
| `action_type` | Select | `server` / `client` / `route` / `modal` / `drawer` / `process` / `report` / `webhook` |
| `handler` | Code | The action implementation (Python function or JS function) |
| `method` | Data | HTTP method for webhook actions |
| `confirm_message` | Text | Optional — confirmation dialog message |
| `visible_when` | Code | Expression controlling visibility |
| `enabled_when` | Code | Expression controlling enabled state |
| `permission` | Link | Permission Rule for access control |
| `audit_required` | Check | Log audit event on execution |
| `refresh_target` | Data | UI element to refresh after execution |
| `priority` | Int | Display priority |

### DocType Process Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `process_type` | Select | `workflow` / `approval` / `generation` / `transformation` / `export` / `import` |
| `parameters` | JSON | Input parameters for the process |
| `handler` | Code | Implementation (Python path) |
| `background` | Check | Whether the process runs in the background |
| `status_tracking` | Check | Track process status with progress updates |
| `retry_policy` | JSON | Retry configuration (max_attempts, backoff) |
| `permission` | Link | Permission Rule for access control |
| `audit_required` | Check | Log audit event on execution |

## 24. Version History

Version History records field-level changes to documents for audit and rollback.

### DocType Version Record Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `docname` | Data | The document that changed |
| `changed_by` | Link | User who made the change |
| `changed_at` | Datetime | When the change occurred |
| `change_type` | Select | `create` / `update` / `submit` / `cancel` / `delete` / `restore` |
| `before` | JSON | Document state before the change |
| `after` | JSON | Document state after the change |
| `diff` | JSON | Field-level diff (fieldname → {old, new}) |
| `comment` | Text | Optional — user-provided change description |
| `source` | Select | `ui` / `api` / `import` / `script` / `migration` |

### Rules

- Version tracking is controlled by the DocType Setting `track_changes`.
- Sensitive fields (marked as password, masked) are excluded from the `diff` or masked in the version record.
- Version retention policy is configurable per site (default: keep all versions).
- Diff is generated at the field level — only changed fields are recorded.

## 25. Comments, Mentions, and Notifications

### Comment Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `docname` | Data | Target document |
| `comment_type` | Select | `comment` / `system` / `workflow` / `assignment` / `integration` / `error` / `audit` |
| `content` | Text | Comment body (Markdown supported) |
| `owner` | Link | User who created the comment |
| `created_at` | Datetime | When the comment was created |
| `edited_at` | Datetime | When the comment was last edited |
| `deleted_at` | Datetime | Soft delete timestamp |
| `visibility` | Select | `public` / `internal` / `restricted` |
| `pinned` | Check | Whether the comment is pinned |
| `resolved` | Check | Whether the comment thread is resolved |

### Mention Model

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `source_doctype` | Link | Source DocType |
| `source_docname` | Data | Source document |
| `comment_id` | Link | Optional — originating comment |
| `mentioned_user` | Link | The user who was mentioned |
| `mentioned_role` | Link | Optional — a role that was mentioned |
| `mentioned_team` | Data | Optional — a team that was mentioned |
| `mentioned_department` | Data | Optional — department that was mentioned |
| `notification_channel` | Select | `in_app` / `email` / `webhook` |
| `mention_type` | Select | `user` / `role` / `team` / `department` / `all` |
| `status` | Select | `pending` / `notified` / `read` / `dismissed` |
| `notified_at` | Datetime | When the notification was sent |
| `read_at` | Datetime | When the mention was read |

### Mention Rules

- `@username` mentions a specific user.
- `@role` mentions all users with that role.
- `@team` mentions all members of a team.
- `@department` mentions all users in a department.
- `@all` mentions everyone with access to the document (must be explicitly allowed in DocType Setting).
- Mention spam prevention: max N mentions per comment (configurable, default 20). Rate-limited at the server level — no more than M mentions per minute per user (configurable, default 30).
- Permission check: mentioned users who cannot access the document are silently skipped. Do not notify users who lack read permission on the document.
- Each valid mention creates a Mention record with status=«pending».
- Mention records track read/unread status per user.
- Support for RTL names and multilingual display names — mentions use the user's display_name field, and @-autocomplete searches across both username and display_name.
- Notifications can be delivered in-app (notification center), by email, or by webhook (configurable per user and per notification rule).
- Mention notification center: a `/desk/notifications` page lists all mentions with read/unread state, grouped by document.
- Email notifications for mentions include a direct link to the document.
- `@all` mentions require `allow_mentions = true` in DocType Setting AND a separate `allow_at_all` flag.

### Notification Rule Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `event` | Select | `on_create` / `on_update` / `on_submit` / `on_cancel` / `on_comment` / `on_mention` / `on_assign` / `on_status_change` |
| `condition` | Code | Optional — expression determining when to notify |
| `notify_roles` | JSON | Roles to notify |
| `notify_users` | JSON | Specific users to notify |
| `notify_owner` | Check | Notify the document owner |
| `message_template` | Text | Jinja2 template for the notification message |
| `channel` | Select | `in_app` / `email` / `webhook` / `all` |
| `enabled` | Check | Whether this rule is active |

## 26. Restrictions by Role / Context

Restrictions limit what users can see or do based on their role and the current context.

### Restriction Dimensions

| Dimension | Examples |
|-----------|----------|
| Role | System Manager, HR Manager, Sales User |
| User | Specific user IDs |
| Site | Different restrictions per site |
| Tenant | Multi-tenant data isolation |
| Branch | Branch-level data visibility |
| Department | Department-level restrictions |
| Record status | Only allow actions on submitted documents |
| Field value | Restrict based on a field value (e.g. `status != "archived"`) |
| Device/IP | Future — restrict based on network location |
| Time window | Future — restrict access during certain hours |

### Restriction Types

| Type | Description |
|------|-------------|
| Read | Prevent seeing records |
| Write | Prevent editing records |
| Delete | Prevent deleting records |
| Create | Prevent creating new records |
| Export | Prevent exporting data |
| Print | Prevent printing |
| Comment | Prevent commenting |
| Action | Prevent executing specific actions |

### Restriction Resolution

```
1. Evaluate role-based restrictions first (highest priority).
2. Evaluate user-based restrictions.
3. Evaluate context-based restrictions (branch, department, status).
4. Evaluate time-based restrictions (if enabled).
5. Most restrictive wins (deny-first).
6. System Manager bypass at role level is configurable.
```

## 27. Integration Hooks

DocType Integrations connect document events to external systems.

### DocType Integration Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `doctype` | Link | Target DocType |
| `integration_type` | Select | `webhook` / `rest_api` / `email` / `file_export` / `external_lookup` / `queue` |
| `event` | Select | `on_create` / `on_update` / `on_delete` / `on_submit` / `on_cancel` / `on_comment` / `scheduled` |
| `endpoint` | Data | URL or queue name |
| `method` | Data | HTTP method (for webhook) |
| `headers` | JSON | Custom headers (secrets referenced by key, not plain values) |
| `payload_template` | Code | Jinja2 template for the outgoing payload |
| `retry_policy` | JSON | Retry configuration |
| `secret_reference` | Data | Key to a secrets store (never store plain secrets in metadata) |
| `enabled` | Check | Whether this integration is active |
| `audit_required` | Check | Log audit event on each integration call |

### Security Rules

- Secrets are never stored in metadata — referenced by key from a secure secrets store.
- All outgoing payloads are validated against a schema before sending.
- Integration errors are logged with full detail.
- Retry policy prevents cascading failures (max attempts, exponential backoff).
- Webhook endpoints must be in an allowlist for security-sensitive instances.

## 28. Utility / Helper Layer

The `galaxy.utils` package provides reusable helpers for the metadata engine.

| Helper | Purpose |
|--------|---------|
| `safe_eval(expr, context)` | Evaluate expressions safely (whitelisted functions only) |
| `normalize_json(value)` | Normalize JSON inputs for consistent storage |
| `validate_naming(name)` | Validate naming convention compliance |
| `slugify(text)` | Convert text to URL-safe slug |
| `format_date(dt, fmt)` | Date/datetime formatting |
| `format_currency(val, currency)` | Currency formatting with symbol |
| `format_number(val, precision)` | Number formatting with precision |
| `validate_field(value, fieldtype)` | Validate a value against a field type definition |
| `apply_mask(value, mask_type)` | Apply a masking rule to a value |
| `evaluate_condition(expr, doc)` | Evaluate a display condition against a document |
| `merge_metadata(base, *layers)` | Merge multiple metadata layers into one |
| `generate_diff(before, after)` | Generate field-level diff between two dicts |
| `log_audit(doctype, docname, action, user)` | Log an audit event |
| `send_notification(user, message, channel)` | Send a notification to a user |
| `serialize_runtimemeta(meta)` | Serialize RuntimeMeta for caching |
| `deserialize_runtimemeta(data)` | Deserialize RuntimeMeta from cache |

## 29. Runtime Metadata Cache

Runtime metadata is cached to avoid repeated database reads on every request.

### Cache Structure

```python
class RuntimeMetaCache:
    _cache: dict[str, RuntimeMeta]  # doctype_name → RuntimeMeta
    _timestamps: dict[str, float]   # doctype_name → cache_time
    _ttl: int = 300                 # default TTL in seconds
```

### Cache Invalidation Triggers

| Trigger | Action |
|---------|--------|
| DocType saved | Clear cache for that doctype |
| Custom Field saved | Clear cache for the target doctype |
| Property Setter saved | Clear cache for the target doctype |
| Permission Rule saved | Clear cache for the target doctype |
| Client Script saved | Clear cache for the target doctype |
| Server Script saved | Clear cache for the target doctype |
| DocType Web View saved | Clear cache for the target doctype |
| Integration saved | Clear cache for the target doctype |
| DocType Override saved | Clear cache for the target doctype |
| App installed / updated | Clear ALL doctype caches |
| Migration applied | Clear ALL doctype caches |
| Theme changed | Clear ALL caches (including view caches) |
| Mention notification sent | No cache impact (notification-only) |
| Comment added | No cache impact |

### Cache Key

```
cache_key = f"runtime_meta:{doctype_name}:{user_role_hash or 'anonymous'}"
```

The user role hash allows caching per-role variants without storing user-specific data in the cache. For user-specific permissions (field-level per-user), the cache falls back to compute-on-demand.

## 30. Security Rules

| Rule | Description |
|------|-------------|
| Never trust client-only validation | All validation is enforced server-side |
| Never let client scripts bypass permissions | Client scripts cannot execute unauthorized server actions |
| Never execute raw SQL from metadata without validation | SQL from Dynamic Field Sources must be validated against dangerous keyword list |
| Always parameterize values | Query parameters must use bound parameters, never string interpolation |
| Always whitelist identifiers | Table names, column names, and field names must be validated against the schema |
| Audit all dangerous operations | Permission changes, script changes, override changes, and privilege escalations are audited |
| Safe error messages for users | Users see generic error messages; admins see detailed logs |
| Generated code is disabled by default | All generated server/client scripts require explicit review and activation |
| Field permissions cannot exceed DocType permissions | Field-level allow cannot override a DocType-level deny |
| Deny wins over allow | For security-sensitive operations, a single deny rule overrides multiple allow rules |
| Secrets never in metadata | API keys, tokens, and passwords are stored in a secure secrets store, referenced by key |
| Expression execution is restricted | Computed field expressions use a safe evaluator, not `eval()` |

## 31. Testing Plan

### Test Categories

| Category | Scope |
|----------|-------|
| Metadata merge tests | Verify RuntimeMeta merge pipeline (base + custom fields + property setters) |
| Property setter tests | Verify property overrides apply correctly with priority resolution |
| Custom field tests | Verify custom fields merge, override base fields, and handle insert_after |
| Field validation tests | Verify all validation rule types and error message collection |
| Computed field tests | Verify safe expression evaluation and dependency tracking |
| Dependency condition tests | Verify show/hide/require/readonly actions based on field values |
| Dynamic source tests | Verify query-based and API-based dynamic options loading |
| Permission tests | Verify DocPerm role-based access control |
| Field-level permission tests | Verify field read/write access control with deny-first resolution |
| Mask rule tests | Verify data masking in list/form/export views |
| Client script loading tests | Verify script loading, versioning, and execution contexts |
| Server script safety tests | Verify blocked imports, SQL validation, and timeout enforcement |
| Version diff tests | Verify field-level diff generation and sensitive field masking |
| Comment/mention permission tests | Verify access control on comments and mentions |
| Integration hook tests | Verify webhook and API integration payload generation |
| Cache invalidation tests | Verify cache clears on metadata changes |
| Multi-dimensional permission tests | Verify role/user/owner/status dimension resolution |
| Override rule tests | Verify controller/service/validation replacement |
| Web view tests | Verify public and token-based document access |
| Action/process tests | Verify action execution, modal display, process tracking |

### Test Infrastructure

```
tests/
├── test_runtimemeta_merge.py      # Metadata merge pipeline
├── test_property_setters.py        # Property setter resolution
├── test_custom_fields.py           # Custom field merge
├── test_validation_rules.py        # Field validation
├── test_computed_fields.py         # Computed field evaluation
├── test_field_dependencies.py      # Field visibility dependencies
├── test_dynamic_sources.py         # Dynamic field options
├── test_permissions.py             # DocPerm + Permission Rules
├── test_field_permissions.py       # Field-level access control
├── test_mask_rules.py              # Data masking
├── test_client_scripts.py          # Client script loading
├── test_server_scripts.py          # Server script safety
├── test_versions.py                # Version diff
├── test_comments.py                # Comment/mention access
├── test_integrations.py            # Integration hooks
├── test_cache.py                   # Cache invalidation
├── test_override_rules.py          # Override resolution
├── test_web_views.py               # Public document access
├── test_actions.py                 # Action/process execution
└── test_security.py                # Security boundary tests
```

## 32. Implementation Phases

### Phase 1: Architecture Document Only

- This document.

### Phase 2: RuntimeMeta Merge Engine

- Implement `get_meta()`, `get_runtime_meta()`, `clear_meta_cache()`.
- Base DocType + DocField loading.
- Custom Field merging.
- Property Setter application.
- DocType Settings loading.
- Cache with TTL and invalidation triggers.
- Test: metadata merge, custom fields, property setters, cache.

### Phase 3: Field Rules

- Field Rule model and validation engine.
- Field Dependency model with multi-condition evaluation.
- Computed Field model with safe expression parser.
- Display Logic model with client-side evaluation.
- Dynamic Field Source model with query/API handlers.
- Test: validation, dependencies, computed fields, dynamic sources.

### Phase 4: Permission Expansion

- Field Permission model and resolution engine.
- Data Mask Rule model and masking engine.
- Permission Rule model with multi-dimensional support.
- Test: field permissions, mask rules, multi-dimensional, permission security.

### Phase 5: Client Scripts and Actions

- Client Script registry and loading.
- Action registry with button/modal/drawer support.
- Process model with background execution.
- Test: script loading, action triggers, process execution.

### Phase 6: Master Field Engine and Export Model

- FieldType registry service — catalog of all field types as metadata (see Doc 29 §4–5).
- Code-aware field types — language mode, editor, lint, security (see Doc 29 §6).
- Enhanced FieldDependency — multi-condition AND/OR groups, expanded operators, UI effects (see Doc 29 §7).
- FieldRule engine — validation, visibility, required, readonly, formatting, styling rules (see Doc 29 §8).
- Safe expression computed field engine — no eval, whitelisted functions (see Doc 29 §10).
- Field permission and data masking engine — role/user level field access (see Doc 29 §12).
- Dynamic options and dynamic source engine — query, API, script, integration sources (see Doc 29 §13).
- Structured export engine — TypeScript, Zod, Yup, Pydantic, Go struct, JSON Schema, OpenAPI (see Doc 29 §14–15).
- React/Vue/Svelte/Next frontend model generation (see Doc 29 §16).
- Code generation blocks integration with protected regions (see Doc 29 §18).
- Tests: FieldType registry, dependencies, rules, computed fields, permissions, masking, export, generation.

### Phase 7: Version, Comments, Mentions, Notifications

- Version history recording with diff generation.
- Comment model with CRUD and permissions.
- Mention model with @-detection and notification creation.
- Notification Rule model with delivery.
- Test: versions, comments, mentions, notifications.

### Phase 8: Integrations and Code Generation

- DocType Integration model with webhook/API handlers.
- Code Generation Block model with template rendering.
- Generated script templates (disabled by default).
- Test: integration hooks, code generation blocks, generated script safety.

### Phase 9: Remaining Components

- DocType Web View with public routing.
- DocType Override with controller replacement.
- DocType Settings UI.
- Utility helpers in `galaxy.utils`.
- Audit logging integration across all components.
- Full end-to-end tests.
- Documentation and migration guides.
