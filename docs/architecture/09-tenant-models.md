# Tenant Models

## Three Models

### 1. One Site = One Database (Current for multi-site)

Each bench site has its own PostgreSQL database. Sites are fully isolated — no shared data.

```
Bench
├── Site A → Database A
├── Site B → Database B
└── Site C → Database C
```

**Best for:** ERP deployments, enterprise customers, data-sensitive apps.

**Implementation:** `galaxy bench create-site` creates a new config with unique PG credentials. Each site's `tab*` tables are in separate databases.

**No tenant_id needed.** Everything in one database belongs to one "tenant" (the site).

---

### 2. Shared Database + tenant_id (Current MVP)

All users across all tenants share one database. A `tenant_id` column on user-facing tables provides isolation.

```
One Database
├── tabUser (tenant_id="TenantA"), tabUser (tenant_id="TenantB")
├── tabReport (tenant_id="TenantA"), tabReport (tenant_id="TenantB")
├── tabSession (tenant_id="TenantA"), tabSession (tenant_id="TenantB")
└── System tables (tabDocType, tabDocField) — no tenant_id, shared globally
```

**Best for:** Simple SaaS apps, MVP, early-stage multi-tenancy.

**Implementation:**
- `current_tenant` context var (thread/request-local)
- Middleware sets tenant from `X-Tenant-ID` header → subdomain → `"Default"`
- All CRUD operations filter/set `tenant_id` via `_tenant_where()` helper
- Auth operations scoped by tenant

**Tenant-scoped tables (`TENANT_TABLES`):**
- `tabUser` — each tenant manages its own users
- `tabSession` — sessions scoped to tenant
- `tabHas Role` — role assignments per tenant
- `tabServer Script` — scripts per tenant
- `tabReport` — reports per tenant
- `tabError Log` — error log per tenant
- `tabTenant` — tenant registry

**Shared tables (no tenant_id):**
- `tabDocType` — schema definitions are global
- `tabDocField` — field definitions are global
- `tabDocPerm` — permission templates are global
- `tabInstalled App` — apps are global
- `tabInstalled Module` — modules are global
- `tabModule Def` — module definitions are global
- `tabRole` — roles are global

**Limitations:**
- No tenant-level resource limits
- One bad query can affect all tenants
- Schema changes affect all tenants simultaneously
- Harder to migrate a single tenant out

---

### 3. PostgreSQL Schema per Tenant (Future)

Each tenant gets its own PostgreSQL schema within the same database.

```
One Database
├── Schema: tenant_a
│   ├── tabUser, tabReport, tabSession, ...
│   └── System tables (tabDocType shared or per-schema)
├── Schema: tenant_b
│   ├── tabUser, tabReport, tabSession, ...
│   └── System tables (tabDocType shared or per-schema)
└── Schema: public (global)
    └── tabDocType, tabDocField, tabDocPerm (shared)
```

**Best for:** Growing SaaS where isolation matters but DB-per-tenant is too expensive.

**Implementation considerations:**
- `search_path` per connection
- Schema-per-tenant creation on tenant signup
- Shared metadata tables in `public` schema
- PostgreSQL `SET search_path TO tenant_a, public`
- Migration DDL must be run per schema

## Tenant Detection (Model 2 Implementation)

Order of precedence in `get_tenant_id(request)`:

1. `X-Tenant-ID` header — explicit tenant override (API clients)
2. Subdomain from `Host` header — `acme.example.com` → tenant `acme`
3. Default — `"Default"` tenant for single-tenant operation

## Tenant Resolution

`resolve_tenant(name_or_domain)` — looks up by both `name` and `domain` in `tabTenant` table. Returns tenant record if found.

## Current Tenant Table

`tabTenant`:
```sql
name        VARCHAR(255) PRIMARY KEY,  -- unique identifier
display_name VARCHAR(255) NOT NULL,
domain      VARCHAR(255),               -- for subdomain detection
status      VARCHAR(50) DEFAULT 'active',
created_at  TIMESTAMP,
updated_at  TIMESTAMP
```

Seeded with one record: `Default` tenant (active, no domain).

## Middleware Integration

```python
class RequireSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        tenant_id = get_tenant_id(request)
        request.state.tenant_id = tenant_id
        current_tenant.set(tenant_id)
        # ... auth checks ...
```

The `current_tenant` context var is available to all downstream functions:
- CRUD operations (filter/create with tenant_id)
- Auth operations (verify_password, create_session, get_session)
- API handlers (via `request.state.tenant_id`)

## CLI

`galaxy tenant list | create | update | delete`

Operates on the `tabTenant` table. Creating a tenant registers it for subdomain/host resolution but does NOT create any database or schema.

## Tenant Admin Note

The Administrator user exists in every tenant? Currently: Administrator is seeded only in the "Default" tenant. Multi-tenant admin strategy is not yet fully designed.

Future: A "super admin" role that can operate across tenants, or tenant-specific admin users created by a management console.