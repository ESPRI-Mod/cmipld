
import typer
from cmipld.cli.config import app as config_app
from cmipld.cli.get import app as get_app

app = typer.Typer()

# Register the subcommands
app.add_typer(config_app)
app.add_typer(get_app)

if __name__ == "__main__":
    app()
