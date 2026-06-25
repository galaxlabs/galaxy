# Milestone 10 — Security Hardening and Runtime Safety

## Goal

Harden the runtime before SaaS, Bench Manager, jobs, plugins, marketplace, or Go support.

## Scope

- protect dangerous APIs with real session auth
- remove fallback Administrator behavior
- CSRF for browser mutations
- server script execution gates
- report SQL execution gates
- safe error response format
- security event log
- login rate limit
- permission test matrix
- secure config defaults

## Dangerous APIs

Protect:

- /desk/*
- /api/resource/*
- /api/migration/*/apply
- /api/core/scripts/*
- /api/report/*
- /api/reports/*
- /api/server-script/*
- /api/scripts/*

## Safe Defaults

- allow_server_scripts = false
- allow_query_reports = false
- allow_script_reports = false
- allow_dev_auth_bypass = false
- csrf_enabled = true
- login_rate_limit_enabled = true

## Acceptance Criteria

- dangerous APIs require valid session
- no fallback Administrator remains
- CSRF enabled for Desk mutations
- scripts/reports disabled by default
- dangerous SQL rejected
- safe error responses
- security events logged
- login rate limit exists
- tests pass
