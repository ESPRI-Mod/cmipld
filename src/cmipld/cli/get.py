
from pathlib import Path
from typing import Any
from cmipld.api.projects import get_all_projects
from cmipld.api.universe import find_terms_in_data_descriptor, find_terms_in_universe, get_all_data_descriptors_in_universe, get_all_terms_in_data_descriptor
from cmipld.core.service.settings import ProjectSettings, ServiceSettings, UniverseSettings
from pydantic import BaseModel
from rich.table import Table
import typer
import re
from rich.json import JSON
from rich.console import Console

app = typer.Typer()
console = Console()
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

## JUST to inventory all possible get : 

"""
UNIVERSE

find_terms_in_data_descriptor(data_descriptor_id: str,
                                  term_id: str,
                                  settings: SearchSettings|None = None) \
                                     -> BaseModel|dict[str: BaseModel]|None:
find_terms_in_universe(term_id: str,
                          settings: SearchSettings|None = None) \
                            -> dict[str, BaseModel]|\
                               dict[str, dict[str, BaseModel]]|\
                               None:
get_all_terms_in_data_descriptor(data_descriptor_id: str) \
                                        -> dict[str, BaseModel]|None:
find_data_descriptors_in_universe(data_descriptor_id: str,
                                     settings: SearchSettings|None = None) \
                                        -> dict|dict[str, dict]|None:
get_all_data_descriptors_in_universe() -> dict[str, dict]:
get_all_terms_in_universe() -> dict[str, dict[str, BaseModel]]:

PROJECT

valid_term_in_collection(value: str,
                             project_id: str,
                             collection_id: str,
                             term_id: str|None = None) \
                               -> bool:
find_terms_in_collection(project_id:str,
                             collection_id: str,
                             term_id: str,
                             settings: SearchSettings|None = None) \
                                -> BaseModel|dict[str: BaseModel]|None:
find_terms_in_project(project_id: str,
                          term_id: str,
                          settings: SearchSettings|None = None) \
                            -> dict[str, BaseModel]|\
                               dict[str, dict[str, BaseModel]]|\
                               None:
get_all_terms_in_collection(project_id: str,
                                collection_id: str)\
                                   -> dict[str, BaseModel]|None:
find_collections_in_project(project_id: str,
                                collection_id: str,
                                settings: SearchSettings|None = None) \
                                    -> dict|dict[str, dict]|None:
get_all_collections_in_project(project_id: str) -> dict[str, dict]|None:
get_all_terms_in_project(project_id: str) -> dict[str, dict[str, BaseModel]]|None:
find_project(project_id: str) -> dict|None:
def get_all_projects() -> dict[str: dict]:

"""


def handle_universe(data_descriptor_id:str|None,term_id:str|None, settings=None):
    print(f"Handling universe with data_descriptor_id={data_descriptor_id}, term_id={term_id}")
    
    if data_descriptor_id and term_id:
        return find_terms_in_data_descriptor(data_descriptor_id,term_id,settings)
    elif term_id:
        return find_terms_in_universe(term_id,settings)
    elif data_descriptor_id:
        return get_all_terms_in_data_descriptor(data_descriptor_id)
    else:
        return get_all_data_descriptors_in_universe().keys()
    


"""
X and Y and options Done
find_terms_in_data_descriptor(data_descriptor_id: str,
                                  term_id: str,
                                  settings: SearchSettings|None = None) \
                                     -> BaseModel|dict[str: BaseModel]|None:
Y and options Done
find_terms_in_universe(term_id: str,
                          settings: SearchSettings|None = None) \
                            -> dict[str, BaseModel]|\
                               dict[str, dict[str, BaseModel]]|\
                               None:
X => Autre command ? list ? find ? 
get_all_terms_in_data_descriptor(data_descriptor_id: str) \
                                        -> dict[str, BaseModel]|None:
X and options Done
find_data_descriptors_in_universe(data_descriptor_id: str,
                                     settings: SearchSettings|None = None) \
                                        -> dict|dict[str, dict]|None:
Nothing
get_all_data_descriptors_in_universe() -> dict[str, dict]:

Nothing... or Nothing + options ? 
get_all_terms_in_universe() -> dict[str, dict[str, BaseModel]]:

"""



def handle_project(project_id:str,collection_id:str|None,term_id:str|None,options=None):
    print(f"Handling project {project_id} with Y={collection_id}, Z={term_id}, options = {options}")

def handle_unknown(x:str|None,y:str|None,z:str|None):
    print(f"Something wrong in X,Y or Z : X={x}, Y={y}, Z={z}")


def display(data:Any):

    if isinstance(data, BaseModel):
        # Pydantic Model
        console.print(JSON.from_data(data.model_dump()))
    elif isinstance(data, dict):
        # Dictionary as JSON
        console.print(JSON.from_data(data))
    elif isinstance(data, list):
        # List as Table
        table = Table(title="List")
        table.add_column("Index")
        table.add_column("Item")
        for i, item in enumerate(data):
            table.add_row(str(i), str(item))
        console.print(table)
    else:
        # Fallback to simple print
        console.print(data)

@app.command()
def get(keys: list[str] = typer.Argument(..., help="List of keys in XXXX:YYYY:ZZZZ format")):
    """
    Command to process a list of keys.
    """
    known_projects = get_all_projects()
    print("know projects :",known_projects)


    # Validate and process each key
    for key in keys:
        validated_key = validate_key_format(key)
        print(f"Processed key: {validated_key}")
        where,what,who = validated_key
        what = what if what!="" else None
        who = who if who!="" else None
        if where == "" or where=="universe": 
            res = handle_universe(what,who)
        elif where in known_projects:
            res = handle_project(where,what,who,{})
        else:
            res = handle_unknown(where,what,who)
        
        display(res)


