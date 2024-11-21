import sys
import logging
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

import cmipld.db as db
import cmipld.utils.settings as settings
import cmipld.utils.functions as functions
from cmipld.models.sqlmodel.mixins import TermKind
from cmipld.models.sqlmodel.project import Collection, Project, PTerm
from cmipld.models.sqlmodel.univers import DataDescriptor, UTerm
from cmipld.utils.functions import read_json_file

_LOGGER = logging.getLogger("project_ingestion")

# TODO: update
def get_collection_filenames(project_dir_path: Path) -> set[Path]:
    # TODO: should be improved.
    result = set(project_dir_path.glob("*.json")) - {
        project_dir_path.joinpath(settings.PROJECT_SPECS_FILENAME)
    }
    return result


def get_data_descriptor_id_from_context(
    collection_id: str, project_context: dict
) -> str:
    data_descriptor_url = project_context[collection_id][
        settings.DATA_DESCRIPTOR_JSON_KEY
    ]
    return Path(data_descriptor_url).name


def get_univers_term(
    data_descriptor_id: str, term_id: str, univers_db_session: Session
) -> tuple[TermKind, dict]:
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


def ingest_collection(collection_filename,
                      project: Project,
                      project_dir_path: Path,
                      project_context: dict,
                      project_db_session, univers_db_session) -> None:
    collection_id = collection_filename.stem
    try:
        data_descriptor_id = get_data_descriptor_id_from_context(
            collection_id, project_context
        )
    except Exception as e:
        _LOGGER.error(f'Unable to parse the data descriptor id for the collection {collection_id}. Skip.\n{str(e)}')
        return
    collection = Collection(
        id=collection_id,
        project=project,
        data_descriptor_id=data_descriptor_id,
    )
    
    try:
        collection_json_file_path = project_dir_path.joinpath(collection_filename)
        collection_json_specs = read_json_file(collection_json_file_path)
    except Exception as e:
        _LOGGER.error(f'Unable to read the collection json file {collection_json_file_path}. Skip.\n{str(e)}')
        return
    
    project_db_session.add(collection)

    try:
        pydantic_class = functions.get_pydantic_class(data_descriptor_id)
    except Exception as e:
        _LOGGER.error(str(e))
        return

    for term_node in collection_json_specs[collection_id]:
        try:
            # DEBUG
            term_id = term_node

            kind, univers_term_json_specs = get_univers_term(
                data_descriptor_id, term_id, univers_db_session
            )
            # project_term_json_specs = instantiate_project_term(univers_term_json_specs,
            #                                                   project_term_json_specs_update,
            #                                                   pydantic_class)

            # DEBUG
            project_term_json_specs = univers_term_json_specs

            term = PTerm(
                id=term_id,
                specs=project_term_json_specs,
                collection=collection,
                kind=kind,
            )
            project_db_session.add(term)
        except NoResultFound:  # TODO: support other cases.
            _LOGGER.error(
                f"fail to find term {term_id} in data descriptor {data_descriptor_id} "
                + f"for the collection {collection_id} of the project {project.id}"
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
        
        try:
            project_context_file_path = project_dir_path.joinpath(settings.CONTEXT_FILENAME)
            project_context = read_json_file(project_context_file_path)
            project_context = project_context[settings.CONTEXT_JSON_KEY]
        except Exception as e:
            msg = f'Unable to read project context file {project_context_file_path}. Abort.'
            _LOGGER.fatal(msg)
            raise RuntimeError(msg) from e

        project = Project(id=project_id, specs=project_json_specs)
        project_db_session.add(project)
        
        for collection_filename in get_collection_filenames(project_dir_path):
            try:
                ingest_collection(collection_filename,
                                  project,
                                  project_dir_path,
                                  project_context,
                                  project_db_session,
                                univers_db_session)
            except Exception as e:
                msg = f'Unexpected error while ingesting collection {collection_filename}. Abort.'
                _LOGGER.fatal(msg)
                raise RuntimeError(msg) from e
        project_db_session.commit()


if __name__ == "__main__":
    ingest_project(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
