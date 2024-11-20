import logging
from pathlib import Path

import cmipld.db as db
from cmipld.models.sqlmodel.mixins import TermKind
from cmipld.models.sqlmodel.univers import DataDescriptor, UTerm
from cmipld.utils.functions import read_json_file
import cmipld.utils.settings as settings

_LOGGER = logging.getLogger("univers_ingestion")

_SKIPED_DIRNAMES = {"_src", "_tests", ".git"}


def get_data_descriptor_ids(univers_dir_path: Path) -> set[str]:
    for _, dir_names, _ in univers_dir_path.walk():
        break
    return set(dir_names) - _SKIPED_DIRNAMES


def infer_term_kind(json_specs: dict) -> TermKind:
    if "pattern" in json_specs:
        return TermKind.PATTERN
    elif "parts" in json_specs:
        return TermKind.COMPOSITE
    else:
        return TermKind.PLAIN


def ingest_data_descriptor(data_descriptor_path: Path) -> None:
    context_file_path = data_descriptor_path.joinpath(settings.CONTEXT_FILENAME)
    try:
        context = read_json_file(context_file_path)
    except Exception as e:
        _LOGGER.error(f'unable to parse {context_file_path}. Skip data descriptor {data_descriptor_path.name}.\n{str(e)}')
        return
    with db.UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptor = DataDescriptor(id=data_descriptor_path.name, context=context)
        session.add(data_descriptor)
        for json_file_name in data_descriptor_path.glob("*.json"):
            json_specs = read_json_file(data_descriptor_path.joinpath(json_file_name))
            kind = infer_term_kind(json_specs)
            term = UTerm(
                id=json_specs["id"],
                specs=json_specs,
                data_descriptor=data_descriptor,
                kind=kind,
            )
            session.add(term)
        session.commit()


def ingest_all(univer_dir_path: Path) -> None:
    data_descriptor_ids = get_data_descriptor_ids(univer_dir_path)
    for data_descriptor_id in data_descriptor_ids:
        ingest_data_descriptor(univer_dir_path.joinpath(data_descriptor_id))

