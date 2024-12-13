import logging
import os
from pathlib import Path
from cmipld.core.service.settings import ServiceSettings
from cmipld.core.service.state import StateService
from cmipld.db import DBConnection
from cmipld.db.models.project import project_create_db
from cmipld.db.models.universe import universe_create_db
from cmipld.db.universe_ingestion import ingest_metadata_universe, ingest_universe
from cmipld.db.project_ingestion import ingest_metadata_project, ingest_project
from rich.logging import RichHandler
from rich.console import Console

_LOGGER = logging.getLogger(__name__)

rich_handler = RichHandler(rich_tracebacks=True)
_LOGGER.addHandler(rich_handler)

def reset_init_all():
    settings_path = "src/cmipld/core/service/settings.toml"
    service_settings = ServiceSettings.load_from_file(settings_path)
    
    if (service_settings.universe.db_path) and os.path.exists(service_settings.universe.db_path):
        os.remove(service_settings.universe.db_path)
    for _, proj in service_settings.projects.items():    
        if (proj.db_path) and os.path.exists(proj.db_path):
            os.remove(proj.db_path)


def init():
    
    settings_path = "src/cmipld/core/service/settings.toml"
    service_settings = ServiceSettings.load_from_file(settings_path)

    # Initialize StateService
    state_service = StateService(service_settings)
    state_service.get_state_summary()
    display(state_service.table())

    state_service.synchronize_all()
    
    # create DB if present in setting and not in described path
    if service_settings.universe.db_path is not None:
        if not os.path.exists(service_settings.universe.db_path):
            os.makedirs(Path(service_settings.universe.db_path).parent,exist_ok=True)
        universe_create_db(Path(service_settings.universe.db_path))
        ingest_metadata_universe(DBConnection(Path(service_settings.universe.db_path)),state_service.universe.local_version) 
    state_service.universe.fetch_versions()
    
    if state_service.universe.db_path and state_service.universe.local_path :
        ingest_universe(Path(state_service.universe.local_path),Path(state_service.universe.db_path))

    display(state_service.table())


    for name,proj_setting in service_settings.projects.items():
        print(f"CREATE DB for project {name}")

        # create project DB if present in setting
        if proj_setting.db_path is not None:
            if not os.path.exists(proj_setting.db_path):
                os.makedirs(Path(proj_setting.db_path).parent,exist_ok=True)
            project_create_db(Path(proj_setting.db_path))
            #ingest_metadata_project(DBConnection(Path(proj_setting.db_path)),state_service.projects[name].local_version)
        state_service.projects[name].fetch_versions()
        print("version local déduite",state_service.projects[name].local_version)
        if proj_setting.db_path and proj_setting.local_path :
            ingest_project(Path(proj_setting.local_path),
                           Path(proj_setting.db_path),
                           state_service.projects[name].local_version)
        state_service.projects[name].fetch_versions()
    display(state_service.table())

def display(table):
    console = Console(record=True,width=200)
    console.print(table)


def test_api():
    from cmipld.api.universe import get_all_terms_in_universe

    all_terms_universe = get_all_terms_in_universe()
    print()
    print(all_terms_universe)


if __name__ == "__main__":
    _LOGGER.setLevel(logging.INFO)

    # print("BEGIN")
    reset_init_all()
    init()
    # print("END")
    
    # print("BEGIN")
    # display_state()
    # print("END")


