# Field Type Dictionary

## Complete Field Type Reference (16 Types)

---

### 1. Data

| Property | Value |
|----------|-------|
| Database column | `VARCHAR(255)` |
| Python type | `str` |
| Validation | Max 255 chars, no newlines |
| Input rendering | Single-line text `<input type="text">` |
| List rendering | Plain text, truncated at 100 chars with tooltip |
| Default handling | `""` (empty string) if None |
| Empty/null behavior | Stored as empty string `''` |
| Import/export | String, CSV-quoted if contains comma |
| Future Go mapping | `string` |

---

### 2. Small Text

| Property | Value |
|----------|-------|
| Database column | `VARCHAR(1024)` |
| Python type | `str` |
| Validation | Max 1024 chars |
| Input rendering | Multi-line `<textarea rows="3">` |
| List rendering | Plain text, truncated at 80 chars |
| Default handling | `""` (empty string) if None |
| Empty/null behavior | Stored as empty string `''` |
| Import/export | String, CSV-quoted |
| Future Go mapping | `string` |

---

### 3. Long Text

| Property | Value |
|----------|-------|
| Database column | `TEXT` |
| Python type | `str` |
| Validation | No length limit |
| Input rendering | Multi-line `<textarea rows="8">` |
| List rendering | Truncated at 120 chars with "..." and expand link |
| Default handling | `""` (empty string) if None |
| Empty/null behavior | Stored as empty string `''` |
| Import/export | String, CSV-quoted |
| Future Go mapping | `string` |

---

### 4. Int

| Property | Value |
|----------|-------|
| Database column | `INTEGER` |
| Python type | `int` |
| Validation | Must be valid integer; coerced via `int(value)` |
| Input rendering | `<input type="number" step="1">` |
| List rendering | Right-aligned number |
| Default handling | `0` if None |
| Empty/null behavior | Stored as `0` |
| Import/export | Integer, no quotes in CSV |
| Future Go mapping | `int32` |

---

### 5. Float

| Property | Value |
|----------|-------|
| Database column | `DOUBLE PRECISION` |
| Python type | `float` |
| Validation | Must be valid number; coerced via `float(value)` |
| Input rendering | `<input type="number" step="any">` |
| List rendering | Right-aligned, 2 decimal places |
| Default handling | `0.0` if None |
| Empty/null behavior | Stored as `0.0` |
| Import/export | Number, no quotes in CSV |
| Future Go mapping | `float64` |

---

### 6. Currency

| Property | Value |
|----------|-------|
| Database column | `DOUBLE PRECISION` |
| Python type | `float` |
| Validation | Same as Float |
| Input rendering | `<input type="number" step="0.01">` with currency symbol prefix |
| List rendering | Right-aligned, 2 decimal places with currency symbol |
| Default handling | `0.0` if None |
| Empty/null behavior | Stored as `0.0` |
| Import/export | Number |
| Future Go mapping | `float64` |

Semantic alias for Float. Same storage, different UI rendering.

---

### 7. Check

| Property | Value |
|----------|-------|
| Database column | `SMALLINT` |
| Python type | `int` (0 or 1) |
| Validation | Coerced via `int(bool(value))` |
| Input rendering | `<input type="checkbox">` |
| List rendering | Checkmark icon or "Yes"/"No" badge |
| Default handling | `0` (unchecked) if None |
| Empty/null behavior | Stored as `0` |
| Import/export | `1`/`0` or `true`/`false` |
| Future Go mapping | `bool` |

---

### 8. Date

| Property | Value |
|----------|-------|
| Database column | `DATE` |
| Python type | `datetime.date` |
| Validation | Valid ISO date string `YYYY-MM-DD` |
| Input rendering | `<input type="date">` |
| List rendering | Formatted as system date format |
| Default handling | `None` if not provided |
| Empty/null behavior | Stored as SQL `NULL` |
| Import/export | ISO format `YYYY-MM-DD` |
| Future Go mapping | `time.Time` |

---

### 9. Datetime

| Property | Value |
|----------|-------|
| Database column | `TIMESTAMP` |
| Python type | `datetime.datetime` |
| Validation | Valid ISO datetime string |
| Input rendering | `<input type="datetime-local">` |
| List rendering | Formatted as system datetime format |
| Default handling | `None` if not provided |
| Empty/null behavior | Stored as SQL `NULL` |
| Import/export | ISO format `YYYY-MM-DD HH:MM:SS` |
| Future Go mapping | `time.Time` |

Time zone handling: Python stores UTC-naive timestamps. Timezone conversion is the application layer's responsibility.

---

### 10. Select

| Property | Value |
|----------|-------|
| Database column | `VARCHAR(255)` |
| Python type | `str` |
| Validation | Value must be one of the options listed in `options` field (newline-separated) |
| Input rendering | `<select>` dropdown with `<option>` for each choice |
| List rendering | Plain text or colored badge |
| Default handling | First option in list if not provided |
| Empty/null behavior | Stored as empty string; fails validation if `reqd` |
| Import/export | String value (must match one of the options) |
| Future Go mapping | `string` |

Options format in `tabDocField.options`: newline-separated list.

Example:
```
Draft
Submitted
Cancelled
```

---

### 11. Link

| Property | Value |
|----------|-------|
| Database column | `VARCHAR(255)` |
| Python type | `str` |
| Validation | No DB-level FK constraint (see policy doc 06) |
| Input rendering | Autocomplete search against target DocType |
| List rendering | Hyperlink to target document |
| Default handling | `""` if not provided |
| Empty/null behavior | Stored as empty string |
| Import/export | Target document name |
| Future Go mapping | `string` |

Target DocType stored in `tabDocField.options`.

No foreign key enforcement in v1. Optional `enforce_foreign_key = true` in metadata for future.

---

### 12. Table (Child Table)

| Property | Value |
|----------|-------|
| Database column | No column — child rows stored in separate table |
| Python type | `list[dict]` |
| Validation | Each child row validated against child DocType fields |
| Input rendering | Dynamic grid/table with add/delete rows |
| List rendering | "N items" link, not directly rendered inline |
| Default handling | `[]` (empty list) if not provided |
| Empty/null behavior | No child rows created |
| Import/export | Nested JSON array of objects |
| Future Go mapping | `[]map[string]any` |

Child DocType has `parent` column referencing parent document name.

---

### 13. Attach

| Property | Value |
|----------|-------|
| Database column | `VARCHAR(512)` |
| Python type | `str` |
| Validation | Must be a valid file path or URL |
| Input rendering | File upload widget with drag-and-drop |
| List rendering | Clickable filename with download icon |
| Default handling | `""` if no file |
| Empty/null behavior | Stored as empty string |
| Import/export | File path relative to site file directory |
| Future Go mapping | `string` |

File storage: Site-local filesystem under `sites/<name>/files/`. Future: S3/GCS via storage backend abstraction.

---

### 14. JSON

| Property | Value |
|----------|-------|
| Database column | `JSONB` |
| Python type | `dict`, `list`, `str`, `int`, `float`, `bool`, `None` |
| Validation | Must be valid JSON; strings auto-serialized via `json.dumps()` |
| Input rendering | Code editor with JSON syntax highlighting |
| List rendering | Pretty-printed JSON truncated at 200 chars |
| Default handling | `None` (SQL NULL) if not provided |
| Empty/null behavior | Stored as SQL `NULL` |
| Import/export | Native JSON, no extra quoting needed |
| Future Go mapping | `any` / `json.RawMessage` |

PostgreSQL `JSONB` supports indexable JSON path queries. Framework stores arbitrary JSON — no schema validation on stored content.

---

### 15. Code

| Property | Value |
|----------|-------|
| Database column | `TEXT` |
| Python type | `str` |
| Validation | No length limit |
| Input rendering | Code editor with monospace font and syntax highlighting |
| List rendering | Truncated first line with "..." indicator |
| Default handling | `""` if not provided |
| Empty/null behavior | Stored as empty string |
| Import/export | String, CSV-quoted |
| Future Go mapping | `string` |

Used for Python scripts, SQL queries. Subject to security validation when executed (see security rules — blocked patterns, blocked modules).

---

### 16. Text (Legacy / Long Text Alias)

| Property | Value |
|----------|-------|
| Database column | `TEXT` |
| Python type | `str` |
| Validation | No length limit |
| Input rendering | Multi-line `<textarea rows="5">` |
| List rendering | Truncated at 120 chars |
| Default handling | `""` if not provided |
| Empty/null behavior | Stored as empty string |
| Import/export | String, CSV-quoted |
| Future Go mapping | `string` |

Behaves identically to Long Text. Semantic alias kept for backward compatibility.

---

## Summary Table

| # | Fieldtype | DB Column | Python | Default | Null Behavior |
|---|-----------|-----------|--------|---------|---------------|
| 1 | Data | `VARCHAR(255)` | `str` | `""` | Empty string |
| 2 | Small Text | `VARCHAR(1024)` | `str` | `""` | Empty string |
| 3 | Long Text | `TEXT` | `str` | `""` | Empty string |
| 4 | Int | `INTEGER` | `int` | `0` | `0` |
| 5 | Float | `DOUBLE PRECISION` | `float` | `0.0` | `0.0` |
| 6 | Currency | `DOUBLE PRECISION` | `float` | `0.0` | `0.0` |
| 7 | Check | `SMALLINT` | `int` (0/1) | `0` | `0` |
| 8 | Date | `DATE` | `date` | `None` | SQL `NULL` |
| 9 | Datetime | `TIMESTAMP` | `datetime` | `None` | SQL `NULL` |
| 10 | Select | `VARCHAR(255)` | `str` | First option | Empty string |
| 11 | Link | `VARCHAR(255)` | `str` | `""` | Empty string |
| 12 | Table | None (child table) | `list[dict]` | `[]` | No rows |
| 13 | Attach | `VARCHAR(512)` | `str` | `""` | Empty string |
| 14 | JSON | `JSONB` | `any` | `None` | SQL `NULL` |
| 15 | Code | `TEXT` | `str` | `""` | Empty string |
| 16 | Text | `TEXT` | `str` | `""` | Empty string |

## Coercion in CRUD

When writing documents through `create_document()` / `update_document()` in `internal/core/crud.py`:

| Fieldtype | Coercion |
|-----------|----------|
| Check | `int(bool(value))` |
| Int | `int(value)` raises `ValueError` on invalid |
| Float, Currency | `float(value)` raises `ValueError` on invalid |
| JSON | `json.dumps()` if not string, with `ensure_ascii=False` |
| All others | Stored as-is (caller must pass correct type) |

## Common Fields on Every DocType

| Field | Type | Purpose |
|-------|------|---------|
| `name` | `VARCHAR(255) PRIMARY KEY` | Auto-generated: `{Doctype}-{timestamp}-{random_hex}` |
| `idx` | `INTEGER DEFAULT 0` | Sort/index position |

System-created tables also have `created_at` and `updated_at` timestamps.

## Tenant-Scoped Tables

Tables in `TENANT_TABLES` also have:

| Field | Type | Purpose |
|-------|------|---------|
| `tenant_id` | `VARCHAR(255) NOT NULL DEFAULT 'Default'` | Tenant isolation scope |

## Future Field Types (Not Yet Implemented)

- **Attach Image** — Like Attach but with image preview and thumbnail generation
- **Color** — Hex color picker, stored as `VARCHAR(7)`
- **Password** — Stored as bcrypt hash, never returned via API
- **Phone** — Validated phone number format, stored as `VARCHAR(20)`
- **Email** — Validated email format, stored as `VARCHAR(255)`
- **Percent** — Like Float but rendered with `%` suffix
- **Rating** — Integer 1–5, rendered as star icons
- **Dynamic Link** — Like Link but `options` field contains a DocField reference instead of a fixed DocType name
- **Read Only** — Like Data but never writable via API; set by server-side logic
- **Signature** — Canvas-based signature capture, stored as image file reference
- **Barcode** — Scanned barcode, stored as `VARCHAR(255)`
- **Geolocation** — JSON `{latitude, longitude}` pair
- **Table MultiSelect** — Like Table but for many-to-many tag selection