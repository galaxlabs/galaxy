# PostgreSQL / MySQL Dialect Differences

## Current State

PostgreSQL 16 is the only supported database. SQLAlchemy Core abstracts basic operations, but DDL and type choices are PG-specific.

## Identifier Quoting

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Quote char | `"identifier"` | `` `identifier` `` |
| Current impl | `f'"{name}"'` | — |

SQLAlchemy Core's `text()` passes identifiers through raw. The framework uses `_quote(name)` in `internal/core/crud.py`.

## Boolean Type

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Native boolean | `BOOLEAN` (stored as `bool`) | `TINYINT(1)` |
| Current impl | `SMALLINT` (0/1) via `int(bool(value))` | — |

Framework stores booleans as `SMALLINT` with client-side coercion. Change to `BOOLEAN` is safe in PG but requires a migration path.

## JSON Type

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Native JSON | `JSONB` (binary, indexed) | `JSON` (5.7+, binary in 8.0+) |
| Current impl | `JSONB` | — |

`JSONB` supports GIN indexes for JSON path queries. MySQL `JSON` uses functional indexes.

## Datetime Type

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Timestamp | `TIMESTAMP` or `TIMESTAMPTZ` | `DATETIME` or `TIMESTAMP` |
| Current impl | `TIMESTAMP` (no tz in DDL) | — |
| Python | `datetime.datetime(UTC)` | — |

PG `TIMESTAMP` without timezone will not convert. Framework handles timezone in Python with `datetime.now(UTC)`.

## Auto Increment / Serial

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Auto column | `SERIAL` / `IDENTITY` | `AUTO_INCREMENT` |
| Current impl | Manual name generation in Python | — |

Framework does not use DB auto-increment. Document `name` values are generated in Python:
```python
f"{doctype_name}-{ts}-{random_hex}"
```

## Index Syntax

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Create | `CREATE INDEX ON table (col)` | `CREATE INDEX ON table (col)` |
| Concurrent | `CREATE INDEX CONCURRENTLY` | `ALTER TABLE ... ADD INDEX` (lock) |
| JSON index | `CREATE INDEX ON table USING GIN (col)` | Functional index with `JSON_EXTRACT` |

## LIMIT / OFFSET

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Syntax | `LIMIT :lim OFFSET :off` | Same |
| Named params | Supported | Supported via SQLAlchemy |

Identical in SQLAlchemy.

## Full Text Search

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Index type | `GIN` with `tsvector` | `FULLTEXT` index |
| Query | `to_tsvector() @@ to_tsquery()` | `MATCH ... AGAINST` |
| Relevance | `ts_rank()` | `MATCH ... AGAINST ... IN BOOLEAN MODE` |

Different implementations. PG supports ranking, highlighting, dictionaries.

## Schema Support

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Schema | `CREATE SCHEMA` | `CREATE DATABASE` (schema = database) |
| Tenant isolation | Schema-per-tenant possible | Database-per-tenant only |

## Migration Safety Considerations for MySQL

Switching to MySQL would require:

- Replace `"` quoting with `` ` `` in all DDL and DML
- Replace `JSONB` with `JSON`
- Replace `SMALLINT` booleans with `TINYINT(1)` or keep SMALLINT
- Verify `LIMIT` / `OFFSET` parameter binding
- Test `VARCHAR(255)` behavior (same in MySQL)
- Test `ON CONFLICT` (MySQL uses `ON DUPLICATE KEY`)
- Test `RETURNING` (MySQL lacks this; use `SELECT LAST_INSERT_ID()`)
- Test `ADD COLUMN IF NOT EXISTS` (MySQL lacks this; use procedural check)

## Dialect Abstraction Plan

Create a `DialectAdapter` class when MySQL support is added:

```python
class DialectAdapter:
    quote_char: str
    boolean_type: str  # "SMALLINT" | "TINYINT(1)" | "BOOLEAN"
    json_type: str      # "JSONB" | "JSON"
    has_returning: bool
    has_if_not_exists: bool

    def quote(self, name: str) -> str: ...
    def add_column_ddl(self, table: str, col_def: str) -> str: ...
    def upsert_sql(self, table: str, ...) -> str: ...
