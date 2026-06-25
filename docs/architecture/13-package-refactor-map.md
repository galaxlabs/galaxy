# 13 — Package Refactor Map

## Goal

Move Galaxy Framework from prototype structure:

```text
cmd/
internal/
sites/
tests/
docs/
```

toward framework package structure:

```text
apps/
  galaxy/
    galaxy/
      cli/
      core/
      desk/
      db/
      auth/
      permissions/
      migration/
      reports/
      scripts/
      bench_manager/
sites/
logs/
config/
tests/
docs/
```

## Rule

Do not move all files at once.

Move one package at a time.

Every move must pass:

```powershell
python -m compileall internal apps
ruff check .
python cmd/galaxy/main.py doctor
pytest
```

## Migration Order

### Step 1 — Scaffold only

Create `apps/galaxy/galaxy/` package folders.

No logic moved.

### Step 2 — Move db package

Move:

```text
internal/db/
→ apps/galaxy/galaxy/db/
```

Update imports.

Run full tests.

### Step 3 — Move core package

Move:

```text
internal/core/
→ apps/galaxy/galaxy/core/
```

Update imports.

Run full tests.

### Step 4 — Move auth package

Move:

```text
internal/core/auth.py or internal/auth/
→ apps/galaxy/galaxy/auth/
```

Run full tests.

### Step 5 — Move desk/http templates carefully

Move Desk-specific logic into:

```text
apps/galaxy/galaxy/desk/
```

Keep server bootstrap stable until all routes are confirmed.

### Step 6 — Move CLI last

Move CLI only after core imports are stable.

## Important Rule

The current working system must remain runnable during the refactor.

No feature changes during package refactor.
No new UI.
No new API.
No migration planner changes.
No permission changes.

Only structure cleanup.

## Verification Before Every Commit

```powershell
python -m compileall internal apps
ruff check .
python cmd/galaxy/main.py doctor
pytest
```