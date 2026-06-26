import typer

from .bench import bench_app
from .doctor import doctor
from .install import install
from .reset import reset
from .start import start
from .tenant import tenant_app

app = typer.Typer(
    name="galaxy",
    help="Galaxy CLI",
)

app.command()(install)
app.command()(doctor)
app.command()(start)
app.command()(reset)
app.add_typer(bench_app)
app.add_typer(tenant_app)

def main():
    app()
