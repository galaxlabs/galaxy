# Galaxy Framework — Vision

## What is Galaxy?

Galaxy is a metadata-driven, full-stack low-code business application framework.
Built with Python and PostgreSQL, it uses metadata tables (DocTypes, Fields, Permissions)
to drive application behavior — no code generation, no transpilation.

The framework is designed for:
- **Business applications** — ERP, CRM, HRMS, project management, inventory
- **Internal tools** — admin panels, dashboards, approval workflows
- **Custom vertical apps** — industry-specific solutions built faster

## Core Philosophy

1. **Metadata is the application.** Define DocTypes in metadata tables;
   the framework reads them to drive CRUD, UI, permissions, and reports.
2. **No code generation.** Metadata is interpreted at runtime, not compiled.
   Changes take effect immediately without rebuilding.
3. **One framework, many apps.** Apps are plugins (Python packages) that provide
   DocTypes, modules, and scripts — all read by the same core engine.
4. **PostgreSQL native.** Every DocType gets a physical table. SQL is direct,
   not abstracted behind an ORM for querying. SQLAlchemy Core is used for
   connection management and parameterized queries only.
5. **Developer-first CLI.** Everything can be done from the command line —
   install, doctor, start, reset. Desk UI is for business users.
6. **Progressive complexity.** Start with metadata → add server scripts →
   add client scripts → add custom API endpoints. Each layer builds on the previous.

## Long-Term Goals

### Stage 1: Bootstrap (Milestones 1-2)
- CLI install/doctor/start/reset
- Core tables with seed data
- Read-only metadata API
- Desk shell with DocType list/detail

### Stage 2: Builder + CRUD (Milestones 3-5)
- DocType Builder (save metadata drafts)
- Migration preview + safe apply
- Generic CRUD engine (read from metadata, write to physical tables)
- Record list and form views in Desk UI

### Stage 3: Customization (Milestones 6-8)
- Server-side scripting (Python hooks on DocType events)
- Client-side scripting (JS hooks on form events)
- Permission engine (role-based row/field level)
- Report builder (query, script, and builder-based reports)

### Stage 4: Platform (Milestones 9-12+)
- Module workspaces and dashboards
- Notification and email engine
- Background job system
- Multi-site management
- Plugin marketplace

## What Galaxy is NOT

- **Not Frappe/ERPNext.** Galaxy is a separate framework built from scratch.
  Frappe/ERPNext conventions (DocType, DocField, DocPerm naming) are used
  because they represent well-tested metadata patterns, not because of framework dependency.
- **Not code-generated.** No code generation step. Metadata is read at runtime.
- **Not a CMS.** Built for structured business data, not content management.
- **Not No-code-only.** Developers can write Python and JS at every layer.

## Principles

- **Explicit over implicit.** Metadata schema is visible in the database,
  not hidden in framework magic.
- **Safe by default.** Migrations preview before apply. Rollback planned.
- **SQL when SQL is better.** For reporting, aggregation, and complex queries,
  raw SQL is preferred over ORM abstraction.
- **Progressively enhanced.** Start simple, add complexity only when needed.
- **Backward compatible.** Metadata schema evolves without breaking existing data.
