from esgvoc.core import service
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

    service.state_service.get_state_summary()
    display(service.state_service.table())

    
