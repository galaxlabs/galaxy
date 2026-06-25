# Milestone 4 — DocType Builder and Migration Planner

## Goal

Admin can create DocType metadata and safely create physical tables.

## Build

- New DocType page
- Add/edit fields
- Save metadata
- Migration preview API
- Migration preview panel in Desk
- Safe apply endpoint
- Apply Migration button in UI
- migration log

## Safety Rule

Never blindly ALTER TABLE.

Allowed first safe operation:

```text
create_table
```

Do not support yet:

- DROP COLUMN
- RENAME COLUMN
- CHANGE TYPE
- ADD UNIQUE
- ADD FOREIGN KEY
- DELETE TABLE

## Acceptance Criteria

- create Customer/Supplier metadata
- preview shows CREATE TABLE SQL
- apply creates physical table
- apply again returns already applied / 409
- migration log exists
- tests pass
