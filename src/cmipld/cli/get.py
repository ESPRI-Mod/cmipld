
from logging import info
from pathlib import Path
from cmipld.api.univers import find_terms_in_univers, get_all_data_descriptors_in_univers
from cmipld.core.service.settings import ProjectSettings, ServiceSettings, UniverseSettings
import typer
import re


app = typer.Typer()

SETTINGS_FILE = Path("./src/cmipld/core/service/settings.toml")

def load_settings() -> ServiceSettings:
    """Load the settings from the TOML file."""
    if SETTINGS_FILE.exists():
        return ServiceSettings.load_from_file(str(SETTINGS_FILE))
    else:
        typer.echo("Settings file not found. Creating a new one with defaults.")
        default_settings = ServiceSettings(
        universe=UniverseSettings(
            github_repo="https://github.com/example/universe",
            branch="main",
            local_path="/local/universe",
            db_name="universe.db"
        ),
        Project1=ProjectSettings(
                project_name="Project1",
                github_repo="https://github.com/example/project1",
                branch="main",
                local_path="/local/project1",
                db_name="project1.db"
            )
        
    )

        default_settings.save_to_file(str(SETTINGS_FILE))
        return default_settings


def validate_key_format(key: str):
    """
    Validate if the key matches the XXXX:YYYY:ZZZZ format.
    """
    if not re.match(r"^\w*:\w*:\w*$", key):
        raise typer.BadParameter(f"Invalid key format: {key}. Must be XXXX:YYYY:ZZZZ.")
    return key.split(":")


def handle_universe(x:str,y:str,z:str):
    print(f"Handling universe with Y={y}, Z={z}")
def handle_project(x:str,y:str,z:str):
    print(f"Handling project {x} with Y={y}, Z={z}")
def handle_unknown(x:str,y:str,z:str):
    print(f"Something wrong in X,Y or Z : X={x}, Y={y}, Z={z}")

DISPATCH_TABLE = {
    ("","","") : handle_universe,
    ("universe","","") : handle_universe,
    ("cmip6plus","","") : handle_project,
    
}
@app.command()
def get(keys: list[str] = typer.Argument(..., help="List of keys in XXXX:YYYY:ZZZZ format")):
    """
    Command to process a list of keys.
    """
    # Validate and process each key
    for key in keys:
        validated_key = validate_key_format(key)
        print(f"Processed key: {validated_key}")
        where,what,who = validated_key
        
        handler = DISPATCH_TABLE.get((where,what,who),handle_unknown)
        handler(where,what,who)


        
