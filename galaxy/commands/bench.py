import os

import typer

from galaxy.bench_manager.platform_db import (
    get_site,
    init_platform_db,
    list_sites,
    site_exists,
    update_site_status,
)
from galaxy.bench_manager.site_manager import (
    backup_site as _backup_site,
)
from galaxy.bench_manager.site_manager import (
    create_site as _create_site,
)
from galaxy.bench_manager.site_manager import (
    delete_site as _delete_site,
)
from galaxy.bench_manager.site_manager import (
    get_site_migration_status as _get_site_migration_status,
)
from galaxy.bench_manager.site_manager import (
    install_app as _install_app,
)
from galaxy.bench_manager.site_manager import (
    list_apps as _list_apps,
)
from galaxy.bench_manager.site_manager import (
    list_backups as _list_backups,
)
from galaxy.bench_manager.site_manager import (
    restore_site as _restore_site,
)
from galaxy.bench_manager.site_manager import (
    uninstall_app as _uninstall_app,
)

bench_app = typer.Typer(name="bench", help="Manage Galaxy sites.")


@bench_app.command()
def init():
    """Initialize the Bench platform database."""
    init_platform_db()
    from galaxy.bench_manager.platform_db import get_platform_db_path
    print("Bench platform database initialized.")
    print(f"  Path: {os.path.normpath(get_platform_db_path())}")


@bench_app.command()
def create_site(
    name: str = typer.Argument(help="Site domain name (e.g. mysite.local)"),
    db_host: str = typer.Option("127.0.0.1", help="PostgreSQL host"),
    db_port: int = typer.Option(5432, help="PostgreSQL port"),
):
    """Create a new Galaxy site."""
    try:
        config = _create_site(name, db_host, db_port)
        print(f"Site '{name}' created.")
        print(f"  Database: {config['db_name']} @ {db_host}:{db_port}")
        print(f"  DB user: {config['db_user']}")
        print(f"  Config: sites/{name}/site_config.json")
        print()
        print("Next steps:")
        print("  1. Create the PostgreSQL database and user (if not auto-managed):")
        print(f"     CREATE DATABASE \\\"{config['db_name']}\\\";")
        print(f"     CREATE USER \\\"{config['db_user']}\\\" WITH PASSWORD '...';")
        print(f"     GRANT ALL PRIVILEGES ON DATABASE \\\"{config['db_name']}\\\" TO \\\"{config['db_user']}\\\";")
        print("  2. Set as default site in common_site_config.json and run:")
        print("     galaxy install")
        print("     galaxy doctor")
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None


@bench_app.command(name="list")
def list_sites_cmd():
    """List all managed sites."""
    sites = list_sites()
    if not sites:
        print("No sites registered.")
        return

    print(f"{'Name':<30} {'Database':<30} {'Status':<15} {'Created':<25}")
    print("-" * 100)
    for s in sites:
        print(f"{s['name']:<30} {s['db_name']:<30} {s['status']:<15} {s['created_at'][:19]:<25}")


@bench_app.command()
def status(name: str = typer.Argument(help="Site name")):
    """Show site status."""
    if not site_exists(name):
        print(f"Site '{name}' not found.")
        raise typer.Exit(1)

    s = get_site(name)
    print(f"Name:      {s['name']}")
    print(f"Database:  {s['db_name']}")
    print(f"DB user:   {s['db_user']}")
    print(f"Status:    {s['status']}")
    print(f"Created:   {s['created_at'][:19]}")
    print(f"Updated:   {s['updated_at'][:19]}")


@bench_app.command()
def delete(name: str = typer.Argument(help="Site name")):
    """Delete a site from the platform (keeps database)."""
    try:
        _delete_site(name)
        print(f"Site '{name}' removed from platform.")
        print("Note: The PostgreSQL database was NOT dropped.")
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None


@bench_app.command()
def doctor():
    """Check status of all managed sites."""
    from galaxy.config import load_site_config
    from galaxy.database.connection import get_engine, test_connection

    print("Galaxy Bench Doctor")
    print()

    sites = list_sites()
    if not sites:
        print("No sites registered. Run 'galaxy bench init' first.")
        return

    print(f"Sites registered: {len(sites)}")
    print()

    for s in sites:
        name = s["name"]
        print(f"  [{name}]")
        print(f"    Status: {s['status']}")
        print(f"    Database: {s['db_name']}")

        try:
            _, site = load_site_config(name)
            engine = get_engine(site)
            if test_connection(engine):
                print("    Connection: OK")
            else:
                print("    Connection: FAILED")
                update_site_status(name, "error")
        except Exception as e:
            print(f"    Connection: ERROR ({e})")
            update_site_status(name, "error")

        print()


@bench_app.command()
def install_app(
    site: str = typer.Argument(help="Site name"),
    app: str = typer.Argument(help="App name"),
):
    """Install an app on a site."""
    try:
        config = _install_app(site, app)
        print(f"App '{app}' installed on site '{site}'.")
        print(f"  Installed apps: {config['installed_apps']}")
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None


@bench_app.command(name="list-apps")
def list_apps_cmd(
    site: str = typer.Argument(help="Site name"),
):
    """List apps installed on a site."""
    try:
        apps = _list_apps(site)
        if not apps:
            print(f"No apps registered for site '{site}'.")
            return
        print(f"{'Name':<20} {'App Name':<20} {'Version':<12} {'Enabled':<8}")
        print("-" * 60)
        for a in apps:
            print(f"{a['name']:<20} {a['app_name']:<20} {a['app_version']:<12} {a['enabled']!s:<8}")
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None


@bench_app.command()
def uninstall_app(
    site: str = typer.Argument(help="Site name"),
    app: str = typer.Argument(help="App name"),
):
    """Remove an app from a site."""
    try:
        config = _uninstall_app(site, app)
        print(f"App '{app}' removed from site '{site}'.")
        print(f"  Installed apps: {config['installed_apps']}")
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None


@bench_app.command()
def backup(
    site: str = typer.Argument(help="Site name"),
):
    """Backup a site database using pg_dump."""
    try:
        result = _backup_site(site)
        print(f"Backup created: {result['path']}")
        print(f"  Size: {result['size']} bytes")
        print(f"  Created: {result['created_at']}")
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None


@bench_app.command(name="list-backups")
def list_backups_cmd(
    site: str = typer.Argument(help="Site name"),
):
    """List backup files for a site."""
    try:
        backups = _list_backups(site)
        if not backups:
            print(f"No backups found for site '{site}'.")
            return
        print(f"{'Filename':<40} {'Size (bytes)':<15} {'Created'}")
        print("-" * 70)
        for b in backups:
            print(f"{b['filename']:<40} {b['size']:<15} {b['created_at']}")
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None


@bench_app.command()
def restore(
    site: str = typer.Argument(help="Site name"),
    backup_path: str = typer.Argument(help="Path to .dump backup file"),
):
    """Restore a site database from a backup using pg_restore."""
    try:
        _restore_site(site, backup_path)
        print(f"Backup restored to site '{site}' from {backup_path}")
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None


@bench_app.command(name="migration-status")
def migration_status_cmd(
    site: str = typer.Argument(help="Site name"),
):
    """Show migration status for all doctypes on a site."""
    try:
        results = _get_site_migration_status(site)
        if not results:
            print(f"No doctypes found for site '{site}' (site may not be installed).")
            return

        pending = sum(1 for r in results if r["migration_status"] == "pending")
        applied = sum(1 for r in results if r["migration_status"] == "applied")

        print(f"Migration status for site '{site}': {applied} applied, {pending} pending")
        print()
        print(f"{'DocType':<25} {'Table':<30} {'Status':<10}")
        print("-" * 65)
        for r in results:
            print(f"{r['name']:<25} {r['table_name']:<30} {r['migration_status']:<10}")
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1) from None
