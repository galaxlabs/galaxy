# Milestone 10 Step 2 — Protect Dangerous APIs

## Goal

Require valid session authentication for dangerous routes.

## Protected Browser Routes

- /desk
- /desk/*

Unauthenticated browser requests redirect to:

```text
/login
```

## Protected API Routes

- /api/resource/*
- /api/migration/*/apply
- /api/core/scripts/*
- /api/report/*
- /api/reports/*
- /api/server-script/*
- /api/scripts/*

Unauthenticated API response:

```json
{
  "success": false,
  "error": "Authentication required."
}
```

HTTP status: 401

## Public Routes

- /
- /health
- /api/version
- /login
- /api/auth/login
- /api/auth/logout
- static assets

## Tests

Add/update tests for:

- GET /desk redirects to /login
- GET /desk/doctypes redirects to /login
- POST /api/resource/Customer returns 401 without session
- GET /api/resource/Customer returns 401 without session
- POST /api/migration/doctype/Customer/apply returns 401 without session
- /health remains public
- /api/version remains public
- /login remains public
- logout without session does not crash
- authenticated session can access protected route

## Acceptance Criteria

- Desk routes require login
- dangerous API routes require login
- public routes still work
- tests pass
