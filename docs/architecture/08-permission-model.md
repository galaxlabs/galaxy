# Permission Model

## Architecture

Role-based DocType-level access control. No row-level or field-level permissions in v1.

```
User → Has Role → Role → DocPerm → DocType
```

## Tables

`tabRole`:
```sql
name VARCHAR(255) PRIMARY KEY,   -- e.g. "System Manager"
role_name VARCHAR(255)
```

`tabHas Role`:
```sql
name VARCHAR(255) PRIMARY KEY,
parent VARCHAR(255) NOT NULL,     -- username
role VARCHAR(255) NOT NULL,       -- role name
tenant_id VARCHAR(255) DEFAULT 'Default'
```

`tabDocPerm`:
```sql
name VARCHAR(255) PRIMARY KEY,
parent VARCHAR(255) NOT NULL,     -- DocType name
role VARCHAR(255) NOT NULL,       -- role name
permlevel INTEGER DEFAULT 0,      -- reserved for hierarchical levels
read BOOLEAN DEFAULT TRUE,
write BOOLEAN DEFAULT FALSE,
create BOOLEAN DEFAULT FALSE,
delete BOOLEAN DEFAULT FALSE
```

## Permission Types

| Type | API Endpoint | Description |
|------|-------------|-------------|
| `read` | GET /api/resource/{doctype} | List documents and get individual documents |
| `write` | PUT /api/resource/{doctype}/{name} | Update existing documents |
| `create` | POST /api/resource/{doctype} | Create new documents |
| `delete` | DELETE /api/resource/{doctype}/{name} | Delete documents |

## Authorization Flow

```
API Handler
  → require_session(request) → extracts username from cookie
  → authorize(doctype, username, perm_type)
    → get_user_roles(username)
      → queries tabHas Role
      → Administrator always returns ["System Manager"]
    → for each role:
      → check_permission(doctype, role, perm_type)
        → queries tabDocPerm WHERE parent=doctype AND role=role AND perm_type=True
        → System Manager always returns True (bypass)
    → if any role grants permission → authorized
    → if no role grants permission → denied
```

## System Manager Bypass

The role name `"System Manager"` is hardcoded as always having full access. This skips the `tabDocPerm` query entirely. This is a shortcut — future versions should store System Manager permissions explicitly in `tabDocPerm`.

## Integration Points

Permissions are checked in `internal/core/api.py`:
- `handle_resource_create` — calls `authorize(doctype, user, "create")`
- `handle_resource_list` — calls `authorize(doctype, user, "read")`
- `handle_resource_get` — calls `authorize(doctype, user, "read")`
- `handle_resource_update` — calls `authorize(doctype, user, "write")`
- `handle_resource_delete` — calls `authorize(doctype, user, "delete")`

## Default Permissions (Seeded)

System Manager role has full CRUD on all 13 DocTypes via 13 `tabDocPerm` records created during `seed_docperms()`.

## Future Enhancements

- Field-level permissions (`permlevel`)
- Row-level permissions (filter queries by user/role/org)
- Role hierarchy (inherit permissions from parent roles)
- Permission caching
- Custom permission scripts

## Tenant Permission Implication

Tenant isolation is handled at the data layer (`tenant_id` filtering in CRUD), not at the permission layer. A user with "read" permission on "Report" can only read reports within their own tenant. Permission and tenant isolation are orthogonal.