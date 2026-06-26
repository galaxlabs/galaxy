# 29 — Master Field Engine and Export Model

## 1. Purpose

Define the architecture for the Galaxy Master Field Engine — a metadata-driven service layer that governs all field behavior across the framework: type registration, rendering, validation, dependencies, permissions, masking, computed values, dynamic options, and structured export to external targets.

## 2. Why Galaxy needs a master Field Engine

Frappe's field system is hardcoded into the framework — field types are Python enums, rendering is coupled to Frappe Desk, and there is no unified service layer for field behavior. Galaxy must support:

- Multiple frontends (React, Vue, Svelte, Next.js, HTMX, mobile)
- Code-aware fields (JS, Python, Go, SQL, HTML, JSON, Markdown, YAML, XML, CSS, Shell, Regex)
- Dynamic field types that can be registered by apps at runtime
- Structured export to TypeScript, Zod, OpenAPI, Pydantic, Go structs, SQL schemas
- Frontend model and form schema generation
- Field behavior that goes beyond Frappe limits (multi-condition dependencies, UI effects, field-level masking, computed expressions)

A master Field Engine decouples field behavior from any single UI framework and makes it a reusable, exportable, inspectable service layer.

## 3. Field Engine vs DocType Engine

The DocType Engine (Doc 23) manages the document lifecycle: metadata merge, CRUD, permissions, migration, caching. The Field Engine manages field-level behavior: what a field is, how it renders, how it validates, how it computes, how it masks, how it exports.

```
DocType Engine                         Field Engine
──────────────                         ───────────
DocType metadata                       FieldType registry
DocField definitions                   Field rendering
DocPerm permissions                    Field validation
CustomField overlay                    Field dependencies
PropertySetter overlay                 Field rules
DocTypeSetting overlay                 Computed fields
RuntimeMeta merge                      Dynamic options
CRUD API                               Field permissions
Permission evaluation                  Field masking
                                       UI schema export
                                       Frontend model generation
                                       Code generation integration
```

The Field Engine is a **consumer** of the DocType Engine. It reads `RuntimeMeta` and provides field-level services. The DocType Engine is **unaware** of the Field Engine — it produces metadata; the Field Engine consumes it.

## 4. FieldType registry

The FieldType registry is a central catalog of all available field types. Each FieldType is defined as metadata, not hardcoded logic.

### FieldType metadata fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Unique identifier (e.g. `Data`, `Int`, `Code`) |
| `label` | String | Human-readable name |
| `category` | String | Category grouping (see §4.1) |
| `database_type` | String | SQL column type (e.g. `VARCHAR`, `INTEGER`, `TEXT`, `JSONB`) |
| `python_type` | String | Python type hint (e.g. `str`, `int`, `float`, `dict`, `bool`) |
| `json_type` | String | JSON Schema type (e.g. `string`, `number`, `integer`, `boolean`, `array`, `object`) |
| `typescript_type` | String | TypeScript type string (e.g. `string`, `number`, `boolean`, `string[]`) |
| `react_component` | String | Default React component name |
| `vue_component` | String | Default Vue component name |
| `svelte_component` | String | Default Svelte component name |
| `html_renderer` | String | Default HTML renderer name |
| `list_renderer` | String | List view renderer name |
| `form_renderer` | String | Form view renderer name |
| `filter_renderer` | String | Filter renderer name |
| `supports_options` | Boolean | Whether field accepts static options |
| `supports_dynamic_options` | Boolean | Whether field supports dynamic options source |
| `supports_validation` | Boolean | Whether field supports validation rules |
| `supports_masking` | Boolean | Whether field supports data masking |
| `supports_permissions` | Boolean | Whether field supports field-level permissions |
| `supports_search` | Boolean | Whether field supports search indexing |
| `supports_export` | Boolean | Whether field supports structured export |
| `supports_import` | Boolean | Whether field supports structured import |
| `supports_computed` | Boolean | Whether field supports computed expressions |
| `supports_code_language` | Boolean | Whether field supports code language mode |
| `default_ui_variant` | String | Default UI variant (e.g. `primary`, `secondary`) |
| `default_width` | String | Default display width (e.g. `full`, `half`, `third`) |
| `default_height` | String | Default display height (e.g. `sm`, `md`, `lg`) |
| `enabled` | Boolean | Whether field type is available for use |

### Registry API

```python
get_field_type(name: str) -> FieldType | None
register_field_type(config: dict) -> FieldType
list_field_types(category: str | None = None) -> list[FieldType]
get_field_type_by_category() -> dict[str, list[FieldType]]
```

Apps register custom field types via:

```python
from galaxy.core.field_engine import registry
registry.register_field_type({
    "name": "Phone",
    "label": "Phone",
    "category": "advanced",
    "python_type": "str",
    "json_type": "string",
    "typescript_type": "string",
    # ...
})
```

### 4.1 FieldType categories

- `basic` — Data, Text, Small Text, Long Text, Read Only, Hidden
- `number` — Int, Float, Decimal, Currency, Percent, Rating, Duration
- `date_time` — Date, Time, Datetime, Date Range, Time Range
- `selection` — Select, Multi Select, Autocomplete, Tag, Checkbox Group, Radio Group
- `boolean` — Check, Switch
- `relation` — Link, Dynamic Link, Table, Table MultiSelect, Tree Link, User Link
- `file` — Attach, Attach Image, Image, Video, Audio, File List, Signature
- `code` — Code, JSON, HTML, Markdown, YAML, XML, CSS, JavaScript, Python, Go, SQL, Shell, Regex
- `web` — URL, Email, Phone, Password, Color, Barcode, QR Code, Geolocation, Map, Web View, IFrame, Rich Text, Editor, Formula, Computed
- `layout` — Section Break, Column Break, Tab Break, Card Break, Accordion, Divider, Spacer, Heading
- `action` — Button, Action Button, Link Button, Modal Trigger, Drawer Trigger
- `computed` — Formula, Computed, Aggregate
- `advanced` — Dynamic Link, Signature, Barcode, QR Code, Geolocation

## 5. FieldType plugin/extension model

Apps can ship custom field types by providing a `field_types.json` or registering via Python API.

### Registration from an app

```json
// apps/my_app/field_types.json
[
    {
        "name": "Phone",
        "label": "Phone",
        "category": "web",
        "database_type": "VARCHAR(20)",
        "python_type": "str",
        "json_type": "string",
        "typescript_type": "string",
        "supports_validation": true,
        "supports_search": true,
        "enabled": true
    }
]
```

### FieldType plugin interface

```python
class FieldTypePlugin:
    name: str
    field_type: str
    def get_config(self) -> dict
    def validate(self, value, field_meta) -> ValidationResult
    def format(self, value, context) -> str
    def coerce(self, value) -> Any
    def export_schema(self, target: str) -> dict
```

## 6. Code-aware field types

Code fields are not simple text fields. Each supports a language mode set via `options.language`.

### Code field options

| Option | Type | Description |
|--------|------|-------------|
| `language` | String | Code language: `js`, `html`, `json`, `python`, `go`, `sql`, `markdown`, `yaml`, `xml`, `css`, `shell`, `regex`, `text` |
| `editor` | String | Editor engine: `plain` (default), `monaco`, `codemirror` (future) |
| `lint_enabled` | Boolean | Enable syntax linting |
| `format_enabled` | Boolean | Enable code formatting |
| `readonly` | Boolean | Read-only editor |
| `min_lines` | Integer | Minimum editor height in lines |
| `max_lines` | Integer | Maximum editor height in lines |
| `allow_execution` | Boolean | Allow code execution (default: `false`) |
| `execution_context` | String | Where execution runs: `client`, `server`, `sandbox` |
| `safe_mode` | Boolean | Restrict dangerous operations |
| `allowed_imports` | Array | Whitelisted import paths |
| `blocked_patterns` | Array | Blocked code patterns (regex) |
| `timeout` | Integer | Execution timeout in ms |

### Code language registry

Each code language maps to:

- Editor syntax highlighting mode
- Validation rules (syntax check, lint)
- Export type metadata
- Security constraints (dangerous APIs blocked by default)

### Security rules

- Code fields do **not** execute by default
- Execution is only possible through explicit Server Script or Client Script engines
- `allow_execution` must be explicitly enabled by an admin
- Dangerous languages/patterns are blocked by default
- `safe_mode` restricts filesystem, network, and subprocess access

## 7. FieldDependency enhancement

The existing `FieldDependency` DocType is expanded to support multi-condition logic, operators, UI effects, and grouped conditions.

### Enhanced FieldDependency metadata

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Unique ID |
| `doctype` | Link | Target DocType |
| `parent` | Data | Parent document (for child table dependencies) |
| `field_name` | Link | Target field |
| `depends_on_field` | Link | Source field to watch |
| `depends_on_value` | Data | Value to compare against |
| `operator` | Select | Comparison operator |
| `action` | Select | Action to perform on match |
| `condition_group` | Data | Group identifier for multi-condition rules |
| `logical_operator` | Select | `AND` / `OR` between conditions in group |
| `priority` | Int | Evaluation priority |
| `enabled` | Boolean | Enable/disable |
| `client_side` | Boolean | Evaluate on client |
| `server_side` | Boolean | Evaluate on server |
| `ui_effect` | Select | Visual effect on match |
| `message` | Text | User-facing message |

### Operators

`equals`, `not_equals`, `contains`, `not_contains`, `starts_with`, `ends_with`, `greater_than`, `less_than`, `greater_or_equal`, `less_or_equal`, `in`, `not_in`, `is_empty`, `is_not_empty`, `regex`, `custom_safe_expression`

### Actions

`show`, `hide`, `mandatory`, `optional`, `read_only`, `editable`, `enable`, `disable`, `set_value`, `clear_value`, `set_options`, `filter_options`, `set_background_color`, `set_text_color`, `set_border_color`, `set_help_text`, `show_warning`, `show_error`, `refresh_field`, `refresh_section`, `refresh_card`, `refresh_tab`

### Multi-condition example

```json
[
    {
        "field_name": "shipping_address",
        "depends_on_field": "requires_shipping",
        "depends_on_value": "1",
        "operator": "equals",
        "action": "show",
        "condition_group": "shipping_group",
        "logical_operator": "AND",
        "priority": 1
    },
    {
        "field_name": "shipping_address",
        "depends_on_field": "order_type",
        "depends_on_value": "physical",
        "operator": "equals",
        "action": "show",
        "condition_group": "shipping_group",
        "logical_operator": "AND",
        "priority": 2
    }
]
```

Both conditions must match (`AND`) for `shipping_address` to be visible.

## 8. FieldRule engine

FieldRule is a wider engine than FieldDependency. Rules define unconditional or condition-based behavior modifications.

### FieldRule types

| Type | Description |
|------|-------------|
| `validation` | Custom validation logic |
| `visibility` | Show/hide field |
| `required` | Make field mandatory/optional |
| `readonly` | Make field read-only/editable |
| `default` | Dynamic default value |
| `computed` | Calculated value expression |
| `formatting` | Value formatting rule |
| `styling` | CSS styling rule |
| `permission` | Field access rule |
| `masking` | Data masking rule |
| `option_filter` | Dynamic option filtering |
| `dynamic_source` | Dynamic options source |
| `action_enablement` | Enable/disable field actions |

### FieldRule metadata

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Unique ID |
| `doctype` | Link | Target DocType |
| `field_name` | Link | Target field |
| `rule_type` | Select | Rule type from list above |
| `condition` | Text | Condition expression |
| `expression` | Text | Value expression |
| `action` | Select | Action to apply |
| `value` | Data | Rule value |
| `message` | Text | User-facing message |
| `severity` | Select | `info`, `warning`, `error`, `blocking` |
| `applies_on` | Select | `client`, `server`, `both` |
| `priority` | Int | Evaluation priority |
| `enabled` | Boolean | Enable/disable |

## 9. Field validation engine

The validation engine applies validations in order:

1. **Type coercion** — convert value to field type
2. **Required check** — if field is mandatory and value is empty
3. **Type validation** — validate value against field type rules
4. **Format validation** — validate format (email, URL, phone, etc.)
5. **Length validation** — min/max length
6. **Range validation** — min/max value
7. **Options validation** — value in allowed options
8. **Regex validation** — pattern match
9. **Unique validation** — unique constraint
10. **FieldRule validation** — custom rule-based validation
11. **FieldDependency validation** — conditional required/readonly

### Validation API

```python
validate_field(field: dict, value: Any, context: dict) -> ValidationResult
coerce_field_value(field: dict, value: Any) -> Any
format_field_value(field: dict, value: Any, context: dict) -> str
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    valid: bool
    coerced_value: Any | None
    errors: list[ValidationError]
    warnings: list[str]
```

## 10. Field calculation/computed engine

Computed fields evaluate safe expressions to produce values.

### ComputedField metadata (enhanced)

| Field | Type | Description |
|-------|------|-------------|
| `doctype` | Link | Target DocType |
| `field_name` | Link | Target field |
| `expression` | Text | Safe expression |
| `dependencies` | JSON | List of field names this expression depends on |
| `compute_on` | Select | `client`, `server`, `both` |
| `store_value` | Boolean | Persist computed value to DB |
| `precision` | Int | Decimal precision |
| `rounding` | Select | `none`, `round`, `ceil`, `floor` |
| `condition` | Text | Optional condition for computation |
| `fallback_value` | Data | Value when computation fails |
| `enabled` | Boolean | Enable/disable |

### Allowed functions

`sum`, `min`, `max`, `average`, `round`, `ceil`, `floor`, `abs`, `date_diff`, `today`, `now`, `concat`, `lower`, `upper`, `length`, `if_else`, `coalesce`, `count`, `distinct`, `weighted_sum`

### Expression examples

- `total = qty * rate`
- `full_name = first_name + " " + last_name`
- `age = date_diff(today(), birth_date)`
- `score = weighted_sum(weights, values)`
- `status_label = if_else(status == "A", "Active", "Inactive")`

### Security

- Never use `eval()` or `exec()` on expressions
- Use a safe expression parser with a whitelist of allowed functions and operators
- Expressions are parsed into AST and executed in a sandbox
- `store_value` must be explicitly set — computed-by-default is client-only

## 11. Field UI rendering engine

The UI rendering engine maps field types and options to UI components.

### Component resolution order

1. Field-specific `component` override
2. FieldType default component for target framework
3. Fallback component

### Renderer API

```python
render_field(field: dict, context: dict) -> RenderedField
```

### RenderedField

```python
@dataclass
class RenderedField:
    component: str
    props: dict
    children: list[RenderedField] | None
    styling: dict
    permissions: dict
    dependencies: list[dict]
    validation: list[dict]
    export_schema: dict | None
```

### UI export schema

Each field can be exported as a UI schema for any target framework:

```json
{
    "name": "customer_name",
    "label": "Customer Name",
    "type": "text",
    "required": true,
    "component": "TextInput",
    "ui": {
        "width": "full",
        "tone": "primary",
        "placeholder": "Enter customer name"
    },
    "validation": [
        { "rule": "required", "message": "Name is required" },
        { "rule": "maxLength", "value": 140 }
    ],
    "dependencies": [],
    "permissions": {
        "read": true,
        "write": true
    }
}
```

## 12. Field permission and masking engine

### Field-level permissions

Field permissions control read/write/export access at the field level.

| Field | Type | Description |
|-------|------|-------------|
| `doctype` | Link | Target DocType |
| `field_name` | Link | Target field |
| `role` | Link | Target role |
| `user` | Link | Specific user override |
| `portal_role` | Data | Portal role restriction |
| `condition` | Text | Additional condition expression |
| `can_read` | Boolean | Allow reading this field |
| `can_write` | Boolean | Allow writing this field |
| `can_export` | Boolean | Allow exporting this field |
| `can_import` | Boolean | Allow importing this field |
| `can_print` | Boolean | Allow printing this field |
| `can_search` | Boolean | Allow searching this field |
| `mask_rule` | Link | Associated data mask rule |
| `priority` | Int | Evaluation priority |
| `enabled` | Boolean | Enable/disable |

**Rule**: Field permission cannot grant access if DocType-level permission denies it. Field permissions are a subset of DocType permissions.

### Data Masking

| Field | Type | Description |
|-------|------|-------------|
| `doctype` | Link | Target DocType |
| `field_name` | Link | Target field |
| `mask_type` | Select | `full`, `partial`, `email`, `phone`, `custom`, `tokenized` |
| `visible_to_roles` | JSON | Roles that can see unmasked value |
| `visible_to_users` | JSON | Users that can see unmasked value |
| `condition` | Text | Condition for mask application |
| `audit_on_reveal` | Boolean | Log when masked value is revealed |
| `enabled` | Boolean | Enable/disable |

### Mask examples

| Mask type | Original | Masked |
|-----------|----------|--------|
| `full` | Abdul Quddos | **** |
| `partial` | Abdul Quddos | Abd******* |
| `email` | abdul@example.com | a***@example.com |
| `phone` | +92-300-1234567 | +92-***-*****7 |
| `tokenized` | Secret123 | tok_abc123xyz |

### Permission API

```python
apply_field_permissions(field: dict, user: dict, context: dict) -> FieldPermissions
apply_masking(field: dict, value: Any, user: dict, context: dict) -> MaskedValue
can_read_field(field: dict, user: dict, context: dict) -> bool
can_write_field(field: dict, user: dict, context: dict) -> bool
```

### FieldPermissions

```python
@dataclass
class FieldPermissions:
    can_read: bool
    can_write: bool
    can_export: bool
    can_import: bool
    can_print: bool
    can_search: bool
    mask: DataMaskRule | None
```

## 13. Dynamic options and dynamic source engine

Fields with `supports_dynamic_options` can load options from external sources.

### DynamicFieldSource metadata

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Unique ID |
| `doctype` | Link | Target DocType |
| `field_name` | Link | Target field |
| `source_type` | Select | `static`, `query`, `api`, `script`, `integration`, `document`, `user_context` |
| `source_handler` | Data | Handler reference (query name, API endpoint, script name) |
| `filters` | JSON | Static filter parameters |
| `depends_on` | JSON | Dynamic filter dependencies |
| `cache_ttl` | Int | Cache TTL in seconds |
| `permission_required` | Select | Required permission to access source |
| `enabled` | Boolean | Enable/disable |

### Source types

- **static** — Options defined in the field's `options` property
- **query** — Options loaded from a named SQL/report query
- **api** — Options fetched from an external API endpoint
- **script** — Options computed by a server script
- **integration** — Options from an integration connector
- **document** — Options from another document's field values
- **user_context** — Options based on user attributes (role, department, etc.)

### Dynamic source API

```python
resolve_dynamic_options(field: dict, document: dict, context: dict) -> list[Option]
resolve_options_for_field(doctype: str, field_name: str, document: dict, context: dict) -> list[Option]
```

### Option format

```json
[
    { "value": "option_1", "label": "Option 1", "group": "Group A", "disabled": false },
    { "value": "option_2", "label": "Option 2", "group": "Group A", "disabled": false }
]
```

## 14. Field export model

Every field can be exported to multiple target formats.

### Export targets

| Target | Description |
|--------|-------------|
| `galaxy_internal` | Internal Galaxy metadata format |
| `json_schema` | JSON Schema draft-07 |
| `openapi_schema` | OpenAPI 3.0 schema object |
| `typescript_interface` | TypeScript interface definition |
| `react_form_schema` | React form field schema |
| `vue_form_schema` | Vue form field schema |
| `svelte_form_schema` | Svelte form field schema |
| `zod_schema` | Zod validation schema code |
| `yup_schema` | Yup validation schema code |
| `pydantic_model` | Pydantic Python model |
| `go_struct` | Go struct definition |
| `sql_create_table` | SQL CREATE TABLE column definition |
| `markdown_docs` | Markdown documentation table |

### Export API

```python
export_field_schema(field: dict, target: str) -> dict | str
export_doctype_schema(doctype: str, target: str) -> dict | str
export_app_schema(app: str, target: str) -> dict[str, dict | str]
```

### TypeScript export example

```typescript
// Generated by Galaxy Field Engine
export interface Customer {
    /** Customer Name */
    customer_name: string;
    /** Email Address */
    email?: string;
    /** Status */
    status?: "Active" | "Inactive" | "Suspended";
    /** Credit Limit */
    credit_limit?: number;
    /** Created At */
    creation: string; // ISO datetime
    /** Modified At */
    modified: string; // ISO datetime
}
```

### React form schema export example

```json
{
    "doctype": "Customer",
    "fields": [
        {
            "name": "customer_name",
            "label": "Customer Name",
            "type": "text",
            "required": true,
            "component": "TextInput",
            "ui": { "width": "full", "tone": "primary" },
            "validation": [
                { "rule": "required", "message": "Customer name is required" },
                { "rule": "maxLength", "value": 140 }
            ]
        },
        {
            "name": "email",
            "label": "Email",
            "type": "email",
            "component": "EmailInput",
            "ui": { "width": "half" },
            "validation": [
                { "rule": "email", "message": "Invalid email format" }
            ]
        }
    ]
}
```

### Zod schema export example

```typescript
import { z } from 'zod';

export const CustomerSchema = z.object({
    customer_name: z.string().min(1, "Customer name is required").max(140),
    email: z.string().email("Invalid email format").optional(),
    status: z.enum(["Active", "Inactive", "Suspended"]).optional(),
    credit_limit: z.number().min(0).optional(),
});
```

### Go struct export example

```go
type Customer struct {
    CustomerName string  `json:"customer_name" validate:"required,max=140"`
    Email        *string `json:"email,omitempty" validate:"omitempty,email"`
    Status       *string `json:"status,omitempty" validate:"omitempty,oneof=Active Inactive Suspended"`
    CreditLimit  *float64 `json:"credit_limit,omitempty" validate:"omitempty,min=0"`
    Creation     string  `json:"creation"`
    Modified     string  `json:"modified"`
}
```

## 15. Frontend model generation

The Field Engine generates frontend-ready models for any supported target framework.

### Model generator API

```python
generate_frontend_model(doctype: str, target: str, options: dict | None = None) -> str
generate_frontend_models(app: str, target: str, options: dict | None = None) -> dict[str, str]
```

### Generation options

```json
{
    "include_system_fields": false,
    "include_permissions": true,
    "include_validation": true,
    "include_relations": true,
    "include_choices": true,
    "use_nullable": true,
    "use_readonly_types": true,
    "export_path": "./generated/models",
    "framework": "react"
}
```

### Output structure for React

```
generated/
    react/
        models/
            Customer.ts
            SalesOrder.ts
            Item.ts
        api/
            customerApi.ts
            salesOrderApi.ts
        forms/
            CustomerForm.tsx
            SalesOrderForm.tsx
        lists/
            CustomerList.tsx
            SalesOrderList.tsx
        validation/
            customerSchema.ts
            salesOrderSchema.ts
        index.ts
```

## 16. React/Vue/Svelte/Next app generation support

The Field Engine schema export is designed to feed into frontend generators. The generation system (Doc 25) uses Field Engine schemas as input data for templates.

### Generation pipeline

```
Metadata → RuntimeMeta → Field Engine Export Schema → Template Engine → Generated Files
```

### Target framework support

| Framework | Models | Forms | Lists | API Client | Validation |
|-----------|--------|-------|-------|------------|------------|
| React | TypeScript | React Hook Form + Zod | React Table | fetch/axios | Zod |
| Vue | TypeScript | VeeValidate + Yup | Vue Table | Axios | Yup |
| Svelte | TypeScript | Svelte Forms | Svelte Table | fetch | Zod |
| Next.js | TypeScript | React Hook Form + Zod | React Table | Server Actions | Zod |
| Plain HTML | — | HTMX | HTML Table | fetch | HTML5 |

### Component mapping

```json
{
    "galaxy_type": "Data",
    "react": "TextInput",
    "vue": "AppInput",
    "svelte": "Input",
    "next": "Input"
}
```

## 17. Structured schema export

Export an entire app's schema as a structured, versioned package.

### Export package structure

```
exports/
    react/
        models/
        api/
        forms/
        lists/
        validation/
    vue/
    svelte/
    next/
    openapi/
    json_schema/
    pydantic/
    go/
    docs/
```

### Metadata export

Each exported package includes a `galaxy.json` manifest:

```json
{
    "galaxy_version": "0.1.0",
    "app": "my_app",
    "export_target": "typescript",
    "exported_at": "2026-01-15T10:30:00Z",
    "doctypes": ["Customer", "SalesOrder", "Item"],
    "schema_version": "1",
    "hash": "abc123def456"
}
```

## 18. Code generation and boilerplate export

The Field Engine connects to the Code Generation system (Doc 25) to produce app boilerplate.

### Generation targets

| Target | Output |
|--------|--------|
| `controller` | Python controller skeleton |
| `service` | Service layer skeleton |
| `api_route` | API route definition |
| `react_form` | React form component |
| `react_list` | React list component |
| `zod_schema` | Zod validation schema |
| `typescript_model` | TypeScript interface |
| `test_skeleton` | Test file skeleton |
| `documentation` | Markdown documentation |
| `integration` | Integration stub |

### CodeGenerationBlock metadata

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Unique ID |
| `doctype` | Link | Source DocType |
| `target_type` | Select | Generation target |
| `language` | Select | Output language |
| `template_engine` | Select | `jinja2`, `handlebars`, `ejs` |
| `template_path` | Data | Template file path |
| `output_path` | Data | Generated file output path |
| `overwrite_policy` | Select | `never`, `always`, `ask`, `diff` |
| `protected_regions` | Boolean | Enable protected region markers |
| `generated_hash` | Data | SHA256 hash of generated content |
| `requires_review` | Boolean | Require review before enabling |
| `enabled` | Boolean | Enable/disable this block |

### Protected regions

Generated files use start/end markers to preserve user edits:

```python
# galaxy:keep:start
# Any code between these markers survives regeneration
# galaxy:keep:end
```

## 19. Security rules

1. **Code fields do not execute by default** — execution requires explicit opt-in via Server Script or Client Script engines
2. **Field permissions are a subset of DocType permissions** — field-level rules cannot override DocType-level restrictions
3. **Dynamic options must check permissions** — sources must not leak data the user cannot access
4. **Field export must respect permissions** — hidden/private fields are excluded unless the export target explicitly permits them
5. **Portal/guest export must respect portal permissions** — restricted views apply
6. **All generated code must be diffed before writing** — no silent overwrites
7. **Generated code affecting runtime behavior requires review** — `requires_review: true` by default for executable output
8. **No raw SQL generation without migration planner review** — schema changes must go through migration pipeline
9. **Safe expression parser** — computed fields never use `eval()` or `exec()`
10. **Masked field access must be audited** — `audit_on_reveal` logging for sensitive fields

## 20. Testing plan

### Unit tests

| Test group | Scope |
|------------|-------|
| FieldType registry | Register, get, list, filter by category |
| Code field language options | Language validation, security defaults |
| FieldDependency conditions | Single, multi-condition, AND/OR groups, operators |
| FieldRule evaluation | All rule types, priority ordering |
| Computed field expressions | Safe evaluation, allowed functions, error handling |
| Dynamic option loading | Static, query, API, script sources |
| Field-level permissions | Read/write/export checks, intersection with DocType perms |
| Data masking | All mask types, role-based unmasking, audit logging |
| UI schema export | Field → schema for each target |
| TypeScript export | Interface generation, type mappings |
| Zod schema export | Schema generation, validation rules |
| React form schema export | Component mapping, UI props |
| OpenAPI/JSON schema export | Schema object generation |
| Go struct export | Struct with tags |
| Generated code protected regions | Preservation on regeneration |
| Export permission filtering | Hidden field exclusion |

### Integration tests

| Test group | Scope |
|------------|-------|
| Full pipeline | Metadata → RuntimeMeta → Field Engine → Export → Generated file |
| Multi-DocType export | App-level schema export |
| Import re-export | Round-trip: export → modify → re-import |

## 21. Implementation phases

### Phase 1 (Current)
- Architecture document (this document)
- Update Doc 23 (DocType Core Engine) to reference Field Engine
- Update Doc 25 (Code Generation) to reference Field Engine export

### Phase 2 — FieldType registry and Field Engine interfaces
- `FieldType` registry dataclass and registry service
- `FieldTypePlugin` interface
- Base `FieldEngine` class with core APIs
- Field type categories and type metadata
- Registry seed data for all required field types
- Tests: registry, plugin interface, type lookup

### Phase 3 — FieldDependency enhancement
- Enhanced FieldDependency metadata schema
- Multi-condition support (AND/OR groups)
- Expanded operator set
- Expanded action set including UI effects
- `evaluate_depends_on(field, document, context)` API
- Client-side and server-side evaluation
- Tests: single, multi-condition, operators, UI effects

### Phase 4 — FieldRule engine
- FieldRule metadata schema
- Rule types: validation, visibility, required, readonly, default, formatting, styling
- `evaluate_field_rules(field, document, context)` API
- Priority-based rule evaluation
- Tests: all rule types, priority ordering, severity

### Phase 5 — Computed field expression engine
- Safe expression parser (no `eval()`)
- Allowed function registry
- `compute_field_value(field, document, context)` API
- Client-side and server-side computation
- `store_value` support with persistence hooks
- Tests: expressions, functions, error handling, edge cases

### Phase 6 — Field permission and masking engine
- Field-level permission metadata and service
- Data mask rule metadata and service
- `apply_field_permissions()`, `apply_masking()` APIs
- Mask types: full, partial, email, phone, custom, tokenized
- Audit logging for masked field reveal
- Tests: permission intersection, all mask types, audit

### Phase 7 — Dynamic options engine
- DynamicFieldSource metadata and registry
- Source types: static, query, api, script, integration, document, user_context
- `resolve_dynamic_options(field, document, context)` API
- Cache layer for dynamic sources
- Permission checks on source access
- Tests: all source types, caching, permission filtering

### Phase 8 — Export Engine
- Export target registry
- `export_field_schema()`, `export_doctype_schema()`, `export_app_schema()` APIs
- TypeScript, Zod, Yup, Pydantic, Go struct, JSON Schema, OpenAPI, SQL exporters
- Permission-filtered export
- Versioned export manifest
- Tests: all export targets, permission filtering, manifest generation

### Phase 9 — Frontend model generation
- `generate_frontend_model()` API for TypeScript
- Model generator for React, Vue, Svelte, Next.js
- Component mapping configuration
- Export package structure
- Tests: model generation, component mapping, package output

### Phase 10 — Code generation integration
- CodeGenerationBlock + Field Engine export integration
- Template engine integration (Jinja2)
- Boilerplate generation: controllers, services, API routes, forms
- Protected region preservation
- Diff preview before write
- Tests: boilerplate generation, protected regions, hash tracking
