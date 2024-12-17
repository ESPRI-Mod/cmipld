
import logging
import os
from pathlib import Path
from esgvoc.core.db import DBConnection
from esgvoc.core.db.models.project import project_create_db
from esgvoc.core.db.models.universe import universe_create_db
from esgvoc.core.db.universe_ingestion import ingest_metadata_universe, ingest_universe
from esgvoc.core.db.project_ingestion import ingest_project
from rich.logging import RichHandler
from rich.console import Console

import esgvoc.core.service as service 

_LOGGER = logging.getLogger(__name__)

rich_handler = RichHandler(rich_tracebacks=True)
_LOGGER.addHandler(rich_handler)


def reset_init_all():
    service_settings = service.service_settings 
    if (service_settings.universe.db_path) and os.path.exists(service_settings.universe.db_path):
        os.remove(service_settings.universe.db_path)
    for _, proj in service_settings.projects.items():    
        if (proj.db_path) and os.path.exists(proj.db_path):
            os.remove(proj.db_path)


def init():
    service_settings = service.service_settings 
    state_service = service.state_service
    state_service.get_state_summary()
    state_service.synchronize_all()
    
    display(state_service.table())
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
        if proj_setting.db_path and proj_setting.local_path :
            ingest_project(project_dir_path=Path(proj_setting.local_path),
                           project_db_file_path=Path(proj_setting.db_path),
                           git_hash=state_service.projects[name].local_version)
        state_service.projects[name].fetch_versions()

    display(state_service.table())


def display(table):
    console = Console(record=True,width=200)
    console.print(table)

if __name__ == "__main__":
    #_LOGGER.setLevel(logging.INFO)

    # print("BEGIN")
    reset_init_all()
    init()
    # print("END")

    # print("BEGIN")
    # display_state()
    # print("END")


