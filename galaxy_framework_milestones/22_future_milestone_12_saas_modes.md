# Future Milestone 12 — SaaS Modes

## Goal

Support subscription SaaS after developer mode is stable.

## Mode 1 — Developer / ERP Mode

```text
one site = one database
```

Best for:

- ERP clients
- consultants
- agencies
- custom DocTypes
- custom migrations

## Mode 2 — End-user SaaS Mode

```text
shared database + tenant_id
```

Best for:

- normal subscription users
- ready-made apps
- no custom migration per user

## Mode 3 — Advanced SaaS Mode

```text
PostgreSQL schema per tenant
```

Best for:

- cloud-managed custom tenants
- medium isolation
- some customization

## Build Order

1. database_per_site first
2. shared tenant_id later
3. schema_per_tenant later
