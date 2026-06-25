# Milestone 5 — Dynamic CRUD API

## Goal

Expose migrated DocTypes through dynamic API.

## Build First

- create_document()
- list_documents()
- get_document()
- POST /api/resource/{doctype}
- GET /api/resource/{doctype}
- GET /api/resource/{doctype}/{name}

## Do Not Build Yet

- PATCH/PUT
- DELETE
- child tables
- import/export
- workflow
- full permissions rewrite

## Required Hardening

- validate DocType exists
- validate physical table exists
- validate fields from metadata
- reject unknown fields
- safe name generation
- safe limit/offset
- safe error response

## Acceptance Criteria

- create/list/get Customer works
- unknown DocType returns 404
- invalid fields rejected
- no stack trace exposed
- tests pass
