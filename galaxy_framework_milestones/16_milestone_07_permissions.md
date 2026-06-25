# Milestone 7 — Permission Engine

## Goal

Enforce access control for API and Desk.

## Build

- role-based DocPerm check
- read/create/write/delete permission
- owner permission where available
- field hidden/read-only behavior where currently supported
- page/module permission later if needed
- permission denied response

## Important

UI hiding is not security. Backend must enforce permissions.

## Required Responses

Unauthorized:

```json
{
  "success": false,
  "error": "Authentication required."
}
```

Forbidden:

```json
{
  "success": false,
  "error": "Permission denied."
}
```

## Acceptance Criteria

- System Manager can manage allowed DocTypes
- normal user cannot access unauthorized DocTypes
- API enforces permission
- Desk respects permission
- tests pass
