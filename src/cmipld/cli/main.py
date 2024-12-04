
import typer
from cmipld.cli.config import app as config_app

app = typer.Typer()

# Register the subcommands
app.add_typer(config_app)

if __name__ == "__main__":
    app()
