import typer

from .doctor import doctor
from .install import install
from .reset import reset
from .start import start

app = typer.Typer(
    name="galaxy",
    help="Galaxy CLI",
)

app.command()(install)
app.command()(doctor)
app.command()(start)
app.command()(reset)

def main():
    app()
