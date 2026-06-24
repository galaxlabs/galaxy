# Galaxy Framework

Metadata-driven full-stack low-code business application framework by Galaxy Labs.

Built with Python, PostgreSQL, Starlette, and SQLAlchemy.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16 (Docker recommended)
- Docker (optional but recommended)

### Setup

```powershell
# 1. Start PostgreSQL via Docker
docker compose up -d

# 2. Install dependencies
pip install -e .

# 3. Install Galaxy Framework site
python cmd\galaxy\main.py install

# 4. Verify installation
python cmd\galaxy\main.py doctor

# 5. Start the server
python cmd\galaxy\main.py start
```

### Verify

```powershell
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/api/version
```

### Reset

```powershell
python cmd\galaxy\main.py reset
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `galaxy install` | Bootstrap a Galaxy Framework site |
| `galaxy doctor`  | Check installation health |
| `galaxy start`   | Start the HTTP server |
| `galaxy reset`   | Drop and recreate core tables |

## Project Structure

```
galaxy-framework/
├── cmd/galaxy/main.py        # CLI entry point
├── internal/
│   ├── cli/                  # Typer CLI commands
│   ├── config/               # Site configuration
│   ├── db/                   # Database layer
│   ├── http/                 # Starlette HTTP server
│   └── bootstrap/            # Installer and doctor
├── sites/                    # Site configs
├── tests/                    # Pytest test suite
└── docs/                     # Milestone documentation
```

## Milestones

- **Milestone 1** — Bootstrap Core (current)
- Milestone 2+ — DocType Builder, CRUD, UI, etc.
