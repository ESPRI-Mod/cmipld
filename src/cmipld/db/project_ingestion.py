import sys
import logging
from pathlib import Path

from pydantic import BaseModel
from sqlmodel import Session, select

import cmipld.db as db
import cmipld.settings as settings
from cmipld import get_pydantic_class
from cmipld.db.models.mixins import TermKind
from cmipld.db.models.project import Collection, Project, PTerm
from cmipld.db.models.univers import DataDescriptor, UTerm
from cmipld.db import read_json_file, items_of_interest

_LOGGER = logging.getLogger("project_ingestion")


def get_data_descriptor_id_from_context(collection_context: dict) -> str:
    data_descriptor_url = collection_context[settings.CONTEXT_JSON_KEY][settings.DATA_DESCRIPTOR_JSON_KEY]
    return Path(data_descriptor_url).name


def get_univers_term(data_descriptor_id: str,
                     term_id: str,
                     univers_db_session: Session) -> tuple[TermKind, dict]:
    statement = (
        select(UTerm)
        .join(DataDescriptor)
        .where(DataDescriptor.id == data_descriptor_id, UTerm.id == term_id)
    )
    results = univers_db_session.exec(statement)
    term = results.one()
    return term.kind, term.specs


def instantiate_project_term(
    univers_term_json_specs: dict,
    project_term_json_specs_update: dict,
    pydantic_class: type[BaseModel],
) -> dict:
    term_from_universe = pydantic_class(**univers_term_json_specs)
    updated_term = term_from_universe.model_copy(
        update=project_term_json_specs_update, deep=True
    )
    return updated_term.model_dump()


def ingest_collection(collection_dir_path: Path,
                      project: Project,
                      project_db_session,
                      univers_db_session) -> None:
    
    collection_id = collection_dir_path.name
    collection_context_file_path = collection_dir_path.joinpath(settings.CONTEXT_FILENAME)
    try:
        
        collection_context = read_json_file(collection_context_file_path)
        data_descriptor_id = get_data_descriptor_id_from_context(collection_context)
    except Exception as e:
        msg = f'Unable to read project context file {collection_context_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e

    try:
        pydantic_class = get_pydantic_class(data_descriptor_id)
    except Exception as e:
        msg = f'Unable to find the pydantic class for data descriptor {data_descriptor_id}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e

    collection = Collection(
        id=collection_id,
        context=collection_context,
        project=project,
        data_descriptor_id=data_descriptor_id,
    )
    project_db_session.add(collection)
    
    for term_file_path in items_of_interest(dir_path=collection_dir_path,
                                            glob_inclusion_pattern='*.json',
                                            exclude_prefixes=settings.SKIPED_FILE_DIR_NAME_PREFIXES,
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
            kind, univers_term_json_specs = get_univers_term(
                    data_descriptor_id, term_id, univers_db_session
                )
            project_term_json_specs = instantiate_project_term(univers_term_json_specs,
                                                               project_term_json_specs,
                                                               pydantic_class)
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


def ingest_project(project_dir_path: Path,
                   project_db_file_path: Path,
                   univers_db_file_path: Path):
    
    try:
        project_connection = db.DBConnection(project_db_file_path)
    except Exception as e:
        msg = f'Unable to read project SQLite file at {project_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    try:
        univers_connection = db.DBConnection(univers_db_file_path)
    except Exception as e:
        msg = f'Unable to read univers SQLite file at {univers_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    
    with project_connection.create_session() as project_db_session,\
         univers_connection.create_session() as univers_db_session:
        
        try:
            project_specs_file_path = project_dir_path.joinpath(settings.PROJECT_SPECS_FILENAME)
            project_json_specs = read_json_file(project_specs_file_path)
            project_id = project_json_specs[settings.PROJECT_ID_JSON_KEY]
        except Exception as e:
            msg = f'Unable to read project specs file  {project_specs_file_path}. Abort.'
            _LOGGER.fatal(msg)
            raise RuntimeError(msg) from e
        
        project = Project(id=project_id, specs=project_json_specs)
        project_db_session.add(project)
        
        for collection_dir_path in items_of_interest(dir_path=project_dir_path,
                                                     exclude_prefixes=settings.SKIPED_FILE_DIR_NAME_PREFIXES,
                                                     kind='dir'):
            try:
                ingest_collection(collection_dir_path,
                                  project,
                                  project_db_session,
                                  univers_db_session)
            except Exception as e:
                msg = f'Unexpected error while ingesting collection {collection_dir_path}. Abort.'
                _LOGGER.fatal(msg)
                raise RuntimeError(msg) from e
        project_db_session.commit()


if __name__ == "__main__":
    #ingest_project(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    ingest_project(db.CMIP6PLUS_DIR_PATH, db.CMIP6PLUS_DB_FILE_PATH, db.UNIVERS_DB_FILE_PATH)
