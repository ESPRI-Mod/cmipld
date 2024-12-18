
import typer
from esgvoc.cli.config import app as config_app
from esgvoc.cli.get import app as get_app
from esgvoc.cli.status import app as status_app

app = typer.Typer()

# Register the subcommands
app.add_typer(config_app)
app.add_typer(get_app)
app.add_typer(status_app)

def main():
    app()
if __name__ == "__main__":
    main()
