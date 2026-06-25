# 15 — Database Support Matrix

## Target

Galaxy uses SQLAlchemy as the database abstraction layer. This document defines the dialect compatibility matrix across supported backends.

## Compatibility Matrix

| Feature                | SQLite                    | PostgreSQL                | MySQL (8.0+)             | MariaDB (10.5+)          | MSSQL (Future)           |
|------------------------|---------------------------|---------------------------|--------------------------|--------------------------|--------------------------|
| **Identifier quoting** | `"double quotes"`         | `"double quotes"`         | `` `backticks` ``        | `` `backticks` ``        | `[brackets]` or `"`      |
| **Boolean type**       | INTEGER 0/1               | BOOLEAN (true/false)      | BOOLEAN (TINYINT(1))     | BOOLEAN (TINYINT(1))     | BIT                      |
| **JSON type**          | TEXT (no native JSON)     | JSONB / JSON              | JSON                     | JSON (from 10.5)         | NVARCHAR(MAX)            |
| **Datetime type**      | TEXT (ISO8601)           | TIMESTAMPTZ               | DATETIME(6)              | DATETIME(6)              | DATETIME2                |
| **Text type**          | TEXT (unlimited)          | TEXT (unlimited)          | LONGTEXT (4GB max)       | LONGTEXT (4GB max)       | NVARCHAR(MAX)            |
| **Auto increment**     | INTEGER PRIMARY KEY       | SERIAL / IDENTITY         | AUTO_INCREMENT           | AUTO_INCREMENT           | IDENTITY                 |
| **Schema support**     | No schema                 | Schemas (public, custom)  | Databases as schemas     | Databases as schemas     | Schemas                  |
| **Full text search**   | FTS5 extension            | tsvector / tsquery        | FULLTEXT index           | FULLTEXT index           | Full-Text Index          |
| **Index syntax**       | Standard SQL              | Standard SQL              | MySQL-specific options   | MySQL-specific options   | Standard SQL             |
| **Migration risk**     | Low (local dev only)     | Low (full DDL support)    | Medium (online DDL)      | Medium (online DDL)      | High (complex DDL)       |
| **Recommended use**    | Local dev, testing, demo  | Production, staging       | Existing infra, legacy   | Existing infra, legacy   | Enterprise-only          |

## Dialect Notes

### SQLite

- No native JSON support. JSON stored as TEXT. `json_extract()` available via function.
- No ALTER TABLE ADD COLUMN with constraints (limited DDL).
- No concurrent writes (single-writer lock).
- No user/role management.
- Full-text search via FTS5 virtual table (separate extension).
- **Use for:** local development, CI tests, learning.

### PostgreSQL (Primary Target)

- Full DDL support including transactional DDL.
- Native JSONB with indexing (jsonb_path_ops, GIN).
- `TIMESTAMPTZ` for timezone-aware datetimes.
- Schemas for multi-tenant isolation (optional).
- `pg_dump`/`pg_restore` for backup.
- Full-text search with `tsvector`/`tsquery`.
- **Use for:** all production deployments.

### MySQL / MariaDB

- Backtick quoting required for identifiers.
- `TINYINT(1)` instead of native BOOLEAN.
- `ALTER TABLE` locks tables in many versions (online DDL in 8.0+).
- Maximum key length limits on TEXT/BLOB indexes.
- `AUTO_INCREMENT` behavior varies with replication.
- JSON type is native but not as feature-rich as JSONB.
- **Use for:** environments where MySQL/MariaDB is mandated.

### MSSQL (Future)

- Requires ODBC driver.
- `NVARCHAR(MAX)` for JSON storage.
- `DATETIME2` for wide date range.
- `IDENTITY` for auto-increment.
- Schema support via `CREATE SCHEMA`.
- Full-text search via separate service.
- **Use for:** enterprise customers with MSSQL requirement only.

## SQLAlchemy Dialect Detection

```python
from sqlalchemy import create_engine, inspect

engine = create_engine(url)
dialect = engine.dialect.name  # "sqlite", "postgresql", "mysql", "mssql"
```

## Future-Proofing Rules

1. All SQL executed through SQLAlchemy text() or core expressions — no raw string concatenation.
2. Identifier quoting handled by SQLAlchemy compiler — never hardcoded.
3. JSON operations use SQLAlchemy `JSON` type or `cast(column, JSON)`.
4. Full-text search abstracted behind a dialect-specific helper per backend.
5. Migration SQL generated per-dialect — never assume PostgreSQL-only syntax in portable code.
6. CI runs tests against SQLite (fast) and PostgreSQL (production parity).