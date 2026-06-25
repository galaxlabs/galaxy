# Galaxy Framework — Phase Overview

## Phase A — Python Core Logic Completion

Goal: complete the framework brain in Python first.

Includes:

- Bench CLI
- Site setup
- One site = one database
- PostgreSQL support
- Core metadata
- DocType / DocField / DocPerm
- Migration planner
- Dynamic CRUD
- Dynamic Desk UI
- Permission engine
- Auth/session
- Server scripts
- Reports
- Security hardening
- Bench Manager later

## Phase B — SaaS / Cloud Layer Later

Goal: support subscription users.

Modes:

1. Developer / ERP mode:
   - one site = one database
   - custom DocTypes and migrations allowed

2. End-user SaaS mode:
   - shared system
   - tenant_id or schema-per-tenant
   - no direct migration by normal user

3. Advanced SaaS mode:
   - schema-per-tenant or database-per-site
   - managed by Bench/Cloud Manager

## Phase C — Go Support Later

Goal: translate proven Python framework logic into Go where useful.

Go should be used later for:

- high-performance runtime
- workers
- realtime
- sync engine
- cloud provisioning agent
- optional compiled API layer
