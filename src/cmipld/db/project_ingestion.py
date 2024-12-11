import logging
from pathlib import Path

from cmipld.core.data_handler import JsonLdResource
from cmipld.core.service.data_merger import DataMerger
from cmipld.db.models.mixins import TermKind
from pydantic import BaseModel

import cmipld.db as db
import cmipld.settings as settings
from cmipld import get_pydantic_class
from cmipld.db import DBConnection, items_of_interest, read_json_file
from cmipld.db.models.project import Collection, Project, PTerm
import cmipld.db.universe_ingestion as universe_ingestion


_LOGGER = logging.getLogger("project_ingestion")

def infer_term_kind(json_specs: dict) -> TermKind:
    if settings.PATTERN_JSON_KEY in json_specs:
        return TermKind.PATTERN
    elif settings.COMPOSITE_JSON_KEY in json_specs:
        return TermKind.COMPOSITE
    else:
        return TermKind.PLAIN


def ingest_metadata_project(connection:DBConnection,git_hash):
    with connection.create_session() as session:
        universe = Project(id=str(connection.file_path.stem), git_hash=git_hash,specs={})
        session.add(universe)    
        session.commit()

###############################
def get_data_descriptor_id_from_context(collection_context: dict) -> str:
    data_descriptor_url = collection_context[settings.CONTEXT_JSON_KEY][settings.DATA_DESCRIPTOR_JSON_KEY]
    return Path(data_descriptor_url).name


def instantiate_project_term(universe_term_json_specs: dict,
                             project_term_json_specs_update: dict,
                             pydantic_class: type[BaseModel]) -> dict:
    term_from_universe = pydantic_class(**universe_term_json_specs)
    updated_term = term_from_universe.model_copy(
        update=project_term_json_specs_update, deep=True
    )
    return updated_term.model_dump()


def ingest_collection(collection_dir_path: Path,
                      project: Project,
                      project_db_session,
                      universe_db_session) -> None:


    collection_id = collection_dir_path.name
    collection_context_file_path = collection_dir_path.joinpath(settings.CONTEXT_FILENAME)
    try:
        collection_context = read_json_file(collection_context_file_path)
        data_descriptor_id = get_data_descriptor_id_from_context(collection_context)
    except Exception as e:
        msg = f'Unable to read project context file {collection_context_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    # [KEEP]
    collection = Collection(
        id=collection_id,
        context=collection_context,
        project=project,
        data_descriptor_id=data_descriptor_id,
        term_kind="") # TODO find term_kind here ? 

    project_db_session.add(collection)
    for term_file_path in collection_dir_path.iterdir():
        _LOGGER.debug(f"found term path : {term_file_path}")
        if term_file_path.is_file() and term_file_path.suffix==".json": 
            try:
                json_specs = DataMerger(data=JsonLdResource(uri =str(term_file_path)),
                                        locally_available={"https://espri-mod.github.io/mip-cmor-tables":".cache/repos/mip-cmor-tables"}).merge_linked_json()[-1]
                term_kind = infer_term_kind(json_specs)
                term_id = json_specs["id"]

            except Exception as e:
                _LOGGER.warning(f'Unable to read term {term_file_path}. Skip.\n{str(e)}')
                continue
            # [KEEP]
            try:
                term = PTerm(
                    id=term_id,
                    specs=json_specs,
                    collection=collection,
                    kind=term_kind,
                )
                project_db_session.add(term)
            except Exception as e:
                _LOGGER.error(
                    f"fail to find term {term_id} in data descriptor {data_descriptor_id} "
                    + f"for the collection {collection_id} of the project {project.id}. Skip {term_id}.\n{str(e)}"
                )
                continue

def ingest_project(project_dir_path: Path,
                   project_db_file_path: Path,
                   universe_db_file_path: Path):
    try:
        project_connection = db.DBConnection(project_db_file_path)
    except Exception as e:
        msg = f'Unable to read project SQLite file at {project_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    try:
        universe_connection = db.DBConnection(universe_db_file_path)
    except Exception as e:
        msg = f'Unable to read universe SQLite file at {universe_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    
    with project_connection.create_session() as project_db_session,\
         universe_connection.create_session() as universe_db_session:
        try:
            project_specs_file_path = project_dir_path.joinpath(settings.PROJECT_SPECS_FILENAME)
            project_json_specs = read_json_file(project_specs_file_path)
            project_id = project_json_specs[settings.PROJECT_ID_JSON_KEY]
        except Exception as e:
            msg = f'Unable to read project specs file  {project_specs_file_path}. Abort.'
            _LOGGER.fatal(msg)
            raise RuntimeError(msg) from e
        
        # [KEEP]
        project = Project(id=project_id, specs=project_json_specs,git_hash="")
        project_db_session.add(project)
        

        for collection_dir_path in project_dir_path.iterdir():
            if collection_dir_path.is_dir() and (collection_dir_path / "000_context.jsonld").exists(): #TODO maybe put that in settings
                _LOGGER.debug(f"found collection dir : {collection_dir_path}")
                try:
                    ingest_collection(collection_dir_path,
                                      project,
                                      project_db_session,
                                      universe_db_session)
                except Exception as e:
                    msg = f'Unexpected error while ingesting collection {collection_dir_path}. Abort.'
                    _LOGGER.fatal(msg)
                    raise RuntimeError(msg) from e
        project_db_session.commit()











################################################

def ingest_collection2(collection_dir_path: Path,
                      project: Project,
                      project_db_session,
                      universe_db_session) -> None:
    
    collection_id = collection_dir_path.name
    collection_context_file_path = collection_dir_path.joinpath(settings.CONTEXT_FILENAME)
    try:
        collection_context = read_json_file(collection_context_file_path)
        data_descriptor_id = get_data_descriptor_id_from_context(collection_context)
    except Exception as e:
        msg = f'Unable to read project context file {collection_context_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    # [KEEP]
    collection = Collection(
        id=collection_id,
        context=collection_context,
        project=project,
        data_descriptor_id=data_descriptor_id)
    

    for term_file_path in items_of_interest(dir_path=collection_dir_path,
                                            glob_inclusion_pattern='*.json',
                                            exclude_prefixes=settings.SKIPPED_FILE_DIR_NAME_PREFIXES,
                                            kind='file'):
        try:
            project_term_json_specs = read_json_file(term_file_path)
        except Exception as e:
            _LOGGER.error(f'Unable to read the term json file {term_file_path}. Skip.\n{str(e)}')
            return
        try:
            term_id = project_term_json_specs[settings.TERM_ID_JSON_KEY]
        except Exception as e:
            _LOGGER.error(f'Term id not found in the term json file {term_file_path}. Skip.\n{str(e)}')
            return
        try:
            kind, universe_term_json_specs = universe_ingestion.get_universe_term(
                    data_descriptor_id, term_id, universe_db_session)
            try:
                term_type = universe_term_json_specs[settings.TERM_TYPE_JSON_KEY]
                pydantic_class = get_pydantic_class(term_type)
            except Exception as e:
                msg = f'Unable to find the pydantic class for term {term_file_path}. Skip.\n{str(e)}'
                _LOGGER.error(msg)
                continue
            
            project_term_json_specs = instantiate_project_term(universe_term_json_specs,
                                                               project_term_json_specs,
                                                               pydantic_class)
            # [KEEP]
            term = PTerm(
                id=term_id,
                specs=project_term_json_specs,
                collection=collection,
                kind=kind,
            )
            project_db_session.add(term)
        except Exception as e:
            _LOGGER.error(
                f"fail to find term {term_id} in data descriptor {data_descriptor_id} "
                + f"for the collection {collection_id} of the project {project.id}. Skip {term_id}.\n{str(e)}"
            )
            continue


def ingest_project2(project_dir_path: Path,
                   project_db_file_path: Path,
                   universe_db_file_path: Path):
    try:
        project_connection = db.DBConnection(project_db_file_path)
    except Exception as e:
        msg = f'Unable to read project SQLite file at {project_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    try:
        universe_connection = db.DBConnection(universe_db_file_path)
    except Exception as e:
        msg = f'Unable to read universe SQLite file at {universe_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    
    with project_connection.create_session() as project_db_session,\
         universe_connection.create_session() as universe_db_session:
        try:
            project_specs_file_path = project_dir_path.joinpath(settings.PROJECT_SPECS_FILENAME)
            project_json_specs = read_json_file(project_specs_file_path)
            project_id = project_json_specs[settings.PROJECT_ID_JSON_KEY]
        except Exception as e:
            msg = f'Unable to read project specs file  {project_specs_file_path}. Abort.'
            _LOGGER.fatal(msg)
            raise RuntimeError(msg) from e
        
        # [KEEP]
        project = Project(id=project_id, specs=project_json_specs)
        project_db_session.add(project)
        
        for collection_dir_path in items_of_interest(dir_path=project_dir_path,
                                                     exclude_prefixes=settings.SKIPPED_FILE_DIR_NAME_PREFIXES,
                                                     kind='dir'):
            try:
                ingest_collection(collection_dir_path,
                                  project,
                                  project_db_session,
                                  universe_db_session)
            except Exception as e:
                msg = f'Unexpected error while ingesting collection {collection_dir_path}. Abort.'
                _LOGGER.fatal(msg)
                raise RuntimeError(msg) from e
        project_db_session.commit()


if __name__ == "__main__":
    ingest_project(db.CMIP6PLUS_DIR_PATH, db.CMIP6PLUS_DB_FILE_PATH, db.UNIVERSE_DB_FILE_PATH)
