# Global Agent Rules

## Work Style

Work one small step at a time.

For every coding milestone, include:

1. Current target path
2. Files to create/edit
3. Exact code
4. Run command
5. How to verify

## Do Not Jump Ahead

Do not add future features unless the milestone asks for them.

Do not build:

- full ERP modules
- SaaS tenant mode
- marketplace
- AI agents
- Go support
- background jobs
- WebSockets

until the foundation is stable.

## Safety Rules

- Never store plain passwords.
- Never expose stack traces to normal API users.
- Never run arbitrary shell commands from UI.
- Use transactions for migrations and seed operations.
- Physical database changes must go through preview/apply flow.
- Dangerous features must be disabled by default.
- Tests must pass before moving forward.

## Verification Standard

Always run:

```powershell
python -m compileall internal cmd
ruff check .
pytest
python cmd/galaxy/main.py doctor
```

When server routes are touched, also run:

```powershell
python cmd/galaxy/main.py start
```
