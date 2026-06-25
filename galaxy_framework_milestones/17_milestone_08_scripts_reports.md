# Milestone 8 — Server Scripts and Report Builder

## Goal

Add controlled automation and reports, but keep them gated.

## Build

- server script metadata
- script execution engine
- report metadata
- query report support
- script report support only behind gate
- Desk pages for scripts/reports if already planned

## Safety Rules

Default dangerous features should be disabled later in Milestone 10.

Server scripts and raw SQL reports are powerful and must not expose stack traces.

## Acceptance Criteria

- basic report can run
- script/report errors are safe
- config gates are prepared or documented
- tests pass
