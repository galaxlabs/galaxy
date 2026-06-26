import json
import os
import random
import string
import subprocess
from datetime import UTC, datetime

from sqlalchemy import text

from galaxy.bench_manager.platform_db import (
    get_site,
    list_sites,
    register_site,
    remove_site,
    site_exists,
)
from galaxy.config import load_site_config
from galaxy.db.connection import get_engine


def _get_sites_dir():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, "sites")


def _generate_password(length=24):
    chars = string.ascii_letters + string.digits
    return "".join(random.SystemRandom().choice(chars) for _ in range(length))


def _site_config_path(name: str) -> str:
    return os.path.join(_get_sites_dir(), name, "site_config.json")


def create_site_config(name: str, db_host: str = "127.0.0.1", db_port: int = 5432):
    db_name = f"galaxy_{name.replace('.', '_').replace('-', '_')}"
    db_user = f"galaxy_{name.replace('.', '_').replace('-', '_')}_user"
    db_password = _generate_password()

    site_dir = os.path.join(_get_sites_dir(), name)
    os.makedirs(site_dir, exist_ok=True)

    common_path = os.path.join(_get_sites_dir(), "common_site_config.json")
    if os.path.exists(common_path):
        with open(common_path) as f:
            common = json.load(f)
    else:
        common = {}

    config = {
        "site_name": name,
        "db_type": "postgres",
        "db_host": db_host,
        "db_port": db_port,
        "db_name": db_name,
        "db_user": db_user,
        "db_password": db_password,
        "installed_apps": common.get("installed_apps", ["core"]),
        "installed_modules": common.get("installed_modules", [
            "Core", "Setup", "Security", "Desk", "Workspace", "Navigation",
        ]),
    }

    config_path = _site_config_path(name)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return config


def create_site(name: str, db_host: str = "127.0.0.1", db_port: int = 5432):
    if site_exists(name):
        raise ValueError(f"Site '{name}' already registered in platform.")

    config = create_site_config(name, db_host, db_port)

    register_site(
        name=name,
        db_name=config["db_name"],
        db_user=config["db_user"],
        config_path=_site_config_path(name),
    )

    return config


def delete_site(name: str):
    if not site_exists(name):
        raise ValueError(f"Site '{name}' not found in platform.")

    site_dir = os.path.join(_get_sites_dir(), name)
    config_path = _site_config_path(name)

    if os.path.exists(config_path):
        os.remove(config_path)

    if os.path.exists(site_dir) and not os.listdir(site_dir):
        os.rmdir(site_dir)

    remove_site(name)


def list_managed_sites():
    return list_sites()


def get_site_info(name: str):
    return get_site(name)


def install_app(site_name: str, app_name: str):
    config_path = _site_config_path(site_name)
    if not os.path.exists(config_path):
        raise ValueError(f"Site '{site_name}' not found. Create the site first with 'galaxy bench create-site'.")

    with open(config_path) as f:
        config = json.load(f)

    installed = config.get("installed_apps", [])
    if app_name in installed:
        raise ValueError(f"App '{app_name}' already installed on site '{site_name}'.")

    installed.append(app_name)
    config["installed_apps"] = installed
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    _, site = load_site_config(site_name)
    engine = get_engine(site)

    with engine.begin() as conn:
        idx = conn.execute(
            text('SELECT COALESCE(MAX(idx), -1) + 1 FROM "tabInstalled App"')
        ).scalar()
        conn.execute(
            text("""
                INSERT INTO "tabInstalled App" (name, app_name, app_version, enabled, idx)
                VALUES (:name, :app_name, :app_version, :enabled, :idx)
                ON CONFLICT (name) DO NOTHING
            """),
            {
                "name": app_name,
                "app_name": app_name,
                "app_version": "0.0.1",
                "enabled": True,
                "idx": idx,
            },
        )

    return config


def list_apps(site_name: str):
    _, site = load_site_config(site_name)
    engine = get_engine(site)

    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT name, app_name, app_version, enabled, idx FROM "tabInstalled App" ORDER BY idx')
        ).mappings().all()
    return [dict(r) for r in rows]


def uninstall_app(site_name: str, app_name: str):
    config_path = _site_config_path(site_name)
    if not os.path.exists(config_path):
        raise ValueError(f"Site '{site_name}' not found.")

    with open(config_path) as f:
        config = json.load(f)

    installed = config.get("installed_apps", [])
    if app_name not in installed:
        raise ValueError(f"App '{app_name}' is not installed on site '{site_name}'.")

    installed.remove(app_name)
    config["installed_apps"] = installed
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    _, site = load_site_config(site_name)
    engine = get_engine(site)

    with engine.begin() as conn:
        conn.execute(
            text('DELETE FROM "tabInstalled App" WHERE name = :name'),
            {"name": app_name},
        )

    return config


def _load_site(site_name: str) -> dict:
    _, site = load_site_config(site_name)
    return site


def _site_engine(site_name: str):
    from galaxy.db.connection import get_engine
    site = _load_site(site_name)
    return get_engine(site)


def _backup_dir(site_name: str) -> str:
    d = os.path.join(_get_sites_dir(), site_name, "backups")
    os.makedirs(d, exist_ok=True)
    return d


def _pg_env(site: dict) -> dict:
    return {**os.environ, "PGPASSWORD": site["db_password"]}


def _check_pg_dump():
    import shutil
    if shutil.which("pg_dump") is None:
        raise RuntimeError("pg_dump not found. Install PostgreSQL client tools and ensure pg_dump is on PATH.")


def _check_pg_restore():
    import shutil
    if shutil.which("pg_restore") is None:
        raise RuntimeError("pg_restore not found. Install PostgreSQL client tools and ensure pg_restore is on PATH.")


def backup_site(site_name: str) -> dict:
    if not site_exists(site_name):
        raise ValueError(f"Site '{site_name}' not found.")

    _check_pg_dump()
    site = _load_site(site_name)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"{site_name}_{ts}.dump"
    backup_path = os.path.join(_backup_dir(site_name), filename)

    result = subprocess.run(
        [
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-acl",
            "--file", backup_path,
            "--host", site["db_host"],
            "--port", str(site["db_port"]),
            "--dbname", site["db_name"],
            "--username", site["db_user"],
        ],
        env=_pg_env(site),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Backup failed: {result.stderr.strip()}")

    return {
        "path": backup_path,
        "filename": filename,
        "size": os.path.getsize(backup_path),
        "created_at": ts,
    }


def list_backups(site_name: str) -> list[dict]:
    if not site_exists(site_name):
        raise ValueError(f"Site '{site_name}' not found.")

    backup_dir = _backup_dir(site_name)
    if not os.path.exists(backup_dir):
        return []

    backups = []
    for f in sorted(os.listdir(backup_dir), reverse=True):
        if f.endswith(".dump"):
            fp = os.path.join(backup_dir, f)
            backups.append({
                "filename": f,
                "path": fp,
                "size": os.path.getsize(fp),
                "created_at": f[:19],
            })
    return backups


def restore_site(site_name: str, backup_path: str):
    if not site_exists(site_name):
        raise ValueError(f"Site '{site_name}' not found.")

    if not os.path.exists(backup_path):
        raise ValueError(f"Backup file not found: {backup_path}")

    _check_pg_restore()
    site = _load_site(site_name)

    result = subprocess.run(
        [
            "pg_restore",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-acl",
            "--host", site["db_host"],
            "--port", str(site["db_port"]),
            "--dbname", site["db_name"],
            "--username", site["db_user"],
            backup_path,
        ],
        env=_pg_env(site),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Restore failed: {result.stderr.strip()}")


def get_site_migration_status(site_name: str) -> list[dict]:
    if not site_exists(site_name):
        raise ValueError(f"Site '{site_name}' not found.")

    engine = _site_engine(site_name)

    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT name, module, app_name, table_name,
                           is_single, is_submittable, is_child_table, is_tree, idx
                    FROM "tabDocType" ORDER BY idx
                """)
            ).mappings().all()
            doctypes = [dict(r) for r in rows]
    except Exception:
        return []

    results = []
    for dt in doctypes:
        table = dt["table_name"]
        with engine.connect() as conn:
            count = conn.execute(
                text("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = :name
                """),
                {"name": table},
            ).scalar()
        status = "applied" if count > 0 else "pending"
        results.append({
            "name": dt["name"],
            "module": dt["module"],
            "app_name": dt["app_name"],
            "table_name": table,
            "is_single": dt["is_single"],
            "is_child_table": dt["is_child_table"],
            "idx": dt["idx"],
            "migration_status": status,
        })

    return results
