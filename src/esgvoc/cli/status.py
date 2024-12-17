from esgvoc.core.service.settings import ServiceSettings
from esgvoc.core.service.state import StateService
import typer
from rich.console import Console

app = typer.Typer()
console = Console()


def display(table):
    console = Console(record=True,width=200)
    console.print(table)



@app.command()
def status():
    """
    Command to display status 
    i.e summary of version of usable ressources (between remote/cached)  
    
    """
    settings_path = "src/esgvoc/core/service/settings.toml"
    service_settings = ServiceSettings.load_from_file(settings_path)

    # Initialize StateService
    state_service = StateService(service_settings)
    state_service.get_state_summary()
    display(state_service.table())
    print(state_service.universe.db_connection)
    for name_proj,state_proj in state_service.projects.items():
        print(state_proj.db_connection)

    