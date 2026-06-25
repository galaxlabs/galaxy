# Future Milestone 13 — Go Support

## Goal

Add Go support after Python framework logic is stable.

## Go Is Not Cancelled

Python proves framework logic.

Go later provides:

- faster runtime
- workers
- realtime services
- cloud provisioning agent
- sync engine
- optional compiled API layer

## Translation Dictionary

Map Python concepts to Go:

- Python dict document → Go map[string]any
- Jinja templates → Go html/template + FuncMap
- SQLAlchemy/Core query → pgx + query builder
- Python hooks → Go interfaces
- Python app loading → Go build-time registry
- migration planner → Go migration planner
- dynamic CRUD → Go resource engine
- permission engine → Go permission checker

## Rule

Do not port unstable features.

Only port after Python version is proven and tested.
