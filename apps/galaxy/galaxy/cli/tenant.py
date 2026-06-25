import typer

from galaxy.config import load_site_config
from galaxy.core.tenant import (
    create_tenant,
    delete_tenant,
    get_tenants,
    resolve_tenant,
    update_tenant,
)
from galaxy.db.connection import get_engine

tenant_app = typer.Typer(name="tenant", help="Manage multi-tenant tenants.")


def _require_engine():
    _, site = load_site_config()
    return get_engine(site)


def _ensure_db():
    from galaxy.db.core_tables import create_core_tables
    engine = _require_engine()
    create_core_tables(engine)
    return engine


@tenant_app.command("list")
def list_tenants():
    """List all tenants."""
    _ensure_db()
    tenants = get_tenants()
    if not tenants:
        typer.echo("No tenants found.")
        raise typer.Exit(0)
    typer.echo(f"{'Name':<20} {'Display Name':<25} {'Domain':<25} {'Status':<10} {'Created':<25}")
    typer.echo("-" * 105)
    for t in tenants:
        created = (t.get("created_at") or "")[:19] if t.get("created_at") else ""
        typer.echo(
            f"{t['name']:<20} {t.get('display_name', ''):<25} "
            f"{t.get('domain', ''):<25} {t.get('status', ''):<10} {created:<25}"
        )


@tenant_app.command("create")
def create_tenant_cmd(
    name: str = typer.Argument(help="Tenant name"),
    display_name: str = typer.Option(None, "--display-name", "-d", help="Human-readable display name"),
    domain: str = typer.Option(None, "--domain", help="Domain for subdomain-based tenant detection"),
):
    """Create a new tenant."""
    _ensure_db()
    existing = resolve_tenant(name)
    if existing:
        typer.echo(f"Tenant '{name}' already exists.", err=True)
        raise typer.Exit(1)
    t = create_tenant(name, display_name=display_name or name, domain=domain or "")
    typer.echo(f"Tenant '{t['name']}' created.")


@tenant_app.command("update")
def update_tenant_cmd(
    name: str = typer.Argument(help="Tenant name"),
    display_name: str = typer.Option(None, "--display-name", "-d", help="New display name"),
    domain: str = typer.Option(None, "--domain", help="New domain"),
    status: str = typer.Option(None, "--status", help="New status (active/inactive)"),
):
    """Update a tenant's display_name, domain, or status."""
    _ensure_db()
    existing = resolve_tenant(name)
    if not existing:
        typer.echo(f"Tenant '{name}' not found.", err=True)
        raise typer.Exit(1)
    t = update_tenant(name, display_name=display_name, domain=domain, status=status)
    typer.echo(f"Tenant '{t['name']}' updated.")


@tenant_app.command("delete")
def delete_tenant_cmd(
    name: str = typer.Argument(help="Tenant name"),
):
    """Delete a tenant."""
    _ensure_db()
    if not delete_tenant(name):
        typer.echo(f"Tenant '{name}' not found.", err=True)
        raise typer.Exit(1)
    typer.echo(f"Tenant '{name}' deleted.")
