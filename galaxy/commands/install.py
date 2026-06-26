import typer

from galaxy.installer import run_install


def install(site: str = typer.Option(None, help="Site name to install (default from config)")):
    """Install Galaxy site."""
    run_install(site)
