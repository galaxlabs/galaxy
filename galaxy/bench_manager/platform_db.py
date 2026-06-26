import os
import sqlite3
from datetime import UTC, datetime


def get_platform_db_path():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, "sites", "platform.db")


def get_connection():
    path = get_platform_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_platform_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sites (
                name TEXT PRIMARY KEY,
                db_name TEXT NOT NULL,
                db_user TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'created',
                site_config_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS bench_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
        conn.execute(
            "INSERT OR IGNORE INTO bench_config (key, value) VALUES (?, ?)",
            ("version", "1"),
        )


def register_site(name: str, db_name: str, db_user: str, config_path: str):
    now = datetime.now(UTC).isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO sites (name, db_name, db_user, status, site_config_path, created_at, updated_at)
               VALUES (?, ?, ?, 'created', ?, ?, ?)""",
            (name, db_name, db_user, config_path, now, now),
        )


def update_site_status(name: str, status: str):
    now = datetime.now(UTC).isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE sites SET status = ?, updated_at = ? WHERE name = ?",
            (status, now, name),
        )


def list_sites():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name, db_name, db_user, status, created_at, updated_at FROM sites ORDER BY name"
        ).fetchall()
    return [dict(r) for r in rows]


def get_site(name: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT name, db_name, db_user, status, created_at, updated_at FROM sites WHERE name = ?",
            (name,),
        ).fetchone()
    return dict(row) if row else None


def remove_site(name: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM sites WHERE name = ?", (name,))


def site_exists(name: str) -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT 1 FROM sites WHERE name = ?", (name,)).fetchone()
    return row is not None
