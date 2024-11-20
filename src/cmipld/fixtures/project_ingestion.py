import logging
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

import cmipld.db as db
import cmipld.utils.settings as settings
from cmipld.models.pydantic import mapping
from cmipld.models.sqlmodel.mixins import TermKind
from cmipld.models.sqlmodel.project import Collection, Project, PTerm
from cmipld.models.sqlmodel.univers import DataDescriptor, UTerm
from cmipld.utils.functions import read_json_file

_LOGGER = logging.getLogger("project_ingestion")


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
    data_descriptor_id: str, term_id: str, session: Session
) -> tuple[TermKind, dict]:
    statement = (
        select(UTerm)
        .join(DataDescriptor)
        .where(DataDescriptor.id == data_descriptor_id, UTerm.id == term_id)
    )
    results = session.exec(statement)
    term = results.one()
    return term.kind, term.specs


def get_pydantic_class(data_descriptor_id: str) -> type[BaseModel]:
    if data_descriptor_id in mapping:
        return mapping[data_descriptor_id]
    else:
        raise Exception(f"{data_descriptor_id} pydantic class not found")


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


def ingest_all(project_dir_path: Path):
    with db.CMIP6PLUS_DB_CONNECTION.create_session() as project_db_session:
        project_json_specs = read_json_file(
            project_dir_path.joinpath(settings.PROJECT_SPECS_FILENAME)
        )
        project = Project(id=project_json_specs[settings.PROJECT_ID_JSON_KEY])
        project_db_session.add(project)
        project_context = read_json_file(
            project_dir_path.joinpath(settings.CONTEXT_FILENAME)
        )
        project_context = project_context[settings.CONTEXT_JSON_KEY]
        with db.UNIVERS_DB_CONNECTION.create_session() as univers_db_session:
            for collection_filename in get_collection_filenames(project_dir_path):
                collection_id = collection_filename.stem
                data_descriptor_id = get_data_descriptor_id_from_context(
                    collection_id, project_context
                )
                collection = Collection(
                    id=collection_id,
                    project=project,
                    data_descriptor_id=data_descriptor_id,
                )
                collection_json_specs = read_json_file(
                    project_dir_path.joinpath(collection_filename)
                )
                project_db_session.add(collection)

                try:
                    pydantic_class = get_pydantic_class(data_descriptor_id)
                except Exception as e:
                    _LOGGER.error(str(e))
                    continue

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
        project_db_session.commit()
