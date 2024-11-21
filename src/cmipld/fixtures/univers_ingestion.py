import sys
import logging
from pathlib import Path

import cmipld.db as db
from cmipld.models.sqlmodel.mixins import TermKind
from cmipld.models.sqlmodel.univers import DataDescriptor, UTerm
from cmipld.utils.functions import read_json_file
import cmipld.utils.settings as settings
from cmipld.errors.ingestion import IngestionError

_LOGGER = logging.getLogger("univers_ingestion")


def get_data_descriptor_ids(univers_dir_path: Path) -> set[str]:
    for _, dir_names, _ in univers_dir_path.walk():
        break
    return set(dir_names) - settings.SKIPED_DIRNAMES


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
            term_file_path = data_descriptor_path.joinpath(json_file_name)
            try:
                json_specs = read_json_file(term_file_path)
            except Exception as e:
                _LOGGER.error(f'unable to read term {term_file_path}. Skip.\n{e}')
                continue
            kind = infer_term_kind(json_specs)
            term = UTerm(
                id=json_specs[settings.TERM_ID_JSON_KEY],
                specs=json_specs,
                data_descriptor=data_descriptor,
                kind=kind,
            )
            session.add(term)
        session.commit()


def ingest_univers(univer_dir_path: Path) -> None:
    try:
        data_descriptor_ids = get_data_descriptor_ids(univer_dir_path)
    except Exception as e:
        msg = f'unable to list data descriptor in {univer_dir_path}'
        _LOGGER.fatal(msg)
        raise IOError(msg) from e
    for data_descriptor_id in data_descriptor_ids:
        try:
            ingest_data_descriptor(univer_dir_path.joinpath(data_descriptor_id))
        except Exception as e:
            msg = f'unexpected error while parsing univers:\n{str(e)}'
            _LOGGER.fatal(msg)
            raise IngestionError(msg) from e


if __name__ == "__main__":
    ingest_univers(Path(sys.argv[1]))