
import typer
from cmipld.cli.config import app as config_app
from cmipld.cli.get import app as get_app
from cmipld.cli.status import app as status_app

app = typer.Typer()

# Register the subcommands
app.add_typer(config_app)
app.add_typer(get_app)
app.add_typer(status_app)

if __name__ == "__main__":
    app()
