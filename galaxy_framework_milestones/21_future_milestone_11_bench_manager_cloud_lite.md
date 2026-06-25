# Future Milestone 11 — Bench Manager / Cloud Lite

## Goal

Create a simple Frappe Press-like management layer.

## Build Later

- Site Manager
- Database Manager
- App Manager
- Module enable/disable
- Migration status
- Backup/restore
- Log viewer
- worker/scheduler status later
- domain/SSL later

## Important Security Rule

Desk UI must not run random shell commands directly.

Flow:

Desk UI
→ Platform API
→ Bench Service
→ safe operation function
→ audit/security log

## User Types

1. Bench Administrator / Platform System Manager
   - can create site
   - can create database
   - can backup/restore
   - can install apps
   - can apply migrations

2. Business Site Manager
   - manages only own business/site
   - cannot manage server/database directly
