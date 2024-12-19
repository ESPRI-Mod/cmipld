import typer
from esgvoc.core.service import esg_voc

app = typer.Typer()

@app.command()
def install():
    """
    Command to clone and build necessary db with the latest available version
    
    """
    esg_voc.install()
    
    
