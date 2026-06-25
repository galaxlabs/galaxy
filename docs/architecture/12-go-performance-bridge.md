# 12 — Go Performance Bridge

## Purpose

Galaxy Framework is Python-first.

Python is the main framework brain:

- Bench CLI
- Site setup
- App registry
- Module registry
- DocType metadata
- DocField metadata
- DocPerm permissions
- Migration planner
- Dynamic CRUD rules
- Desk UI
- Auth/session
- Server scripts
- Reports
- Tenant rules

Go is not the main framework core now.

Go may be added later as a performance bridge for heavy repeated operations after the Python architecture is proven and tested.

---

## Main Architecture

```
Python Galaxy Framework
  ↓ validates request
  ↓ checks session
  ↓ checks permission
  ↓ checks tenant
  ↓ builds safe operation
Go Performance Engine
  ↓ executes fast operation
PostgreSQL
```

Python is the control plane.

Go is the data plane.

---

## What Python Keeps

Python keeps all dynamic framework logic:

- metadata loading
- DocType behavior
- field validation rules
- migration planning
- permission decisions
- tenant context
- script safety
- report definitions
- Desk rendering
- app/module install rules

---

## What Go Can Handle Later

Go can handle only hot paths:

- fast list query execution
- fast create/update/get/delete
- bulk CSV/XLSX import
- bulk export
- report result streaming
- background workers
- realtime notification hub
- search indexing

---

## What Go Must Not Do

Go must not become an unsafe SQL executor.

Bad request:

```json
{
  "sql": "SELECT * FROM \"tabCustomer\""
}
```

Good request:

```json
{
  "doctype": "Customer",
  "operation": "list",
  "fields": ["name", "customer_name", "status"],
  "filters": [
    ["status", "=", "Active"]
  ],
  "limit": 20,
  "offset": 0
}
```

---

## Required Go Validation

Even if Python validates first, Go must re-check:

- DocType exists
- table is applied/migrated
- fields exist in metadata
- requested fields are allowed
- filters use allowed operators
- limit is capped
- tenant filter is present when required
- values are parameterized
- no raw SQL is accepted

---

## API Contract Between Python and Go

Python sends safe structured operation:

```json
{
  "site": "gogal.dev",
  "tenant_id": "Default",
  "user": "Administrator",
  "doctype": "Customer",
  "operation": "list",
  "fields": ["name", "customer_name", "status"],
  "filters": [
    ["status", "=", "Active"]
  ],
  "order_by": "created_at desc",
  "limit": 20,
  "offset": 0
}
```

Go returns standard response:

```json
{
  "success": true,
  "data": []
}
```

Error response:

```json
{
  "success": false,
  "error": "Safe error message."
}
```

---

## First Go Bridge Candidate

Do not start with full CRUD.

First candidate should be:

```
Read-only list operation
```

Route later:

```
POST /go-engine/resource/list
```

Reason:

- easier to test
- no write risk
- useful for performance
- safe before create/update/delete

---

## Development Rule

Do not write Go bridge code until:

```
Python CRUD API is stable
Permission engine is stable
Tenant isolation is tested
Field type dictionary is complete
Migration safety rules are complete
Python-to-Go translation dictionary is complete
```

---

## Final Decision

Galaxy Framework stays Python-first.

Go is optional and performance-focused.

Python must keep working even if Go engine is disabled.

Fallback rule:

```
If Go engine fails, Python engine handles the request.
```