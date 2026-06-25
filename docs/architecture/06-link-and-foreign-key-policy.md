# Link and Foreign Key Policy

## Policy (v1)

**Do not create hard foreign keys automatically.**

A Link field stores the target document's `name` as plain text. No `REFERENCES` constraint is created in PostgreSQL.

## Rationale

1. **DocType independence** — Changing or deleting a referenced DocType should not cascade to all tables that link to it.
2. **Cross-site and cross-tenant reference** — A link may reference a document outside the current tenant or even a different database.
3. **Soft deletion** — Hard FK prevents keeping orphan-safe records.
4. **Dynamic schema** — User-created DocTypes should not require superuser-level ALTER permissions for FK creation.

## How It Works

A Link field like:
```
DocField: { fieldname: "customer", fieldtype: "Link", options: "Customer" }
```

Stores a text value in the column `customer VARCHAR(255)` that references `Customer.name`. No database-level constraint enforces this relationship.

## Application-Level Reference Checking

When `enforce_foreign_key` is enabled in metadata (future feature), the framework will:
1. Check the referenced document exists on INSERT/UPDATE
2. Block deletion if referenced by other documents (soft)
3. This is done via SELECT queries, not DB constraints

## Performance Implications

- No FK means no automatic index on link columns. Indexes must be created explicitly (future feature via DocField metadata).
- JOINs between DocType tables are done in Python or SQL at the application level, not via DB relationships.
- The CRUD engine does NOT automatically resolve Link fields to their display values — that's the role of the Desk UI layer.

## Future Foreign Key Options

```json
{
    "fieldname": "customer",
    "fieldtype": "Link",
    "options": "Customer",
    "enforce_foreign_key": true,
    "cascade_delete": false,
    "cascade_update": false
}
```

When `enforce_foreign_key = true`:

| DB | Generated DDL |
|----|--------------|
| PostgreSQL | `customer VARCHAR(255) REFERENCES "tabCustomer"(name)` |
| MySQL | `` customer VARCHAR(255) REFERENCES `tabCustomer`(name) `` |

## UUID / Autoname Consideration

Since document names are auto-generated as `{DocType}-{timestamp}-{hex}`, all Link values are text strings that follow this format. No numeric ID or UUID is needed.

## Current Implementation

- `tabDocField.options` stores the target DocType name for Link fields.
- No validation on Link value at the CRUD level.
- Link fields appear as select/dropdown in Desk UI (future feature: populate options from target DocType).