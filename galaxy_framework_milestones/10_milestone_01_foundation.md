# Milestone 1 — Python Core Foundation

## Goal

Create the first working foundation.

## Build

- galaxy CLI
- galaxy install
- galaxy doctor
- galaxy start / serve
- site config
- PostgreSQL connection
- core bootstrap tables
- Administrator user
- System Manager role
- installed app/module seed

## Site Model

Use:

```text
one site = one database
```

Files:

```text
sites/common_site_config.json
sites/galaxy.local/site_config.json
```

## Required Tables

- tabInstalled App
- tabInstalled Module
- tabModule Def
- tabUser
- tabRole
- tabHas Role

## Acceptance Criteria

- install creates config files
- PostgreSQL connection works
- core tables exist
- app/module seed exists
- Administrator user exists with hashed password
- Administrator has System Manager role
- doctor prints OK
- health route works
- version route works
- compileall, ruff, tests pass
