import sys
import logging
from pathlib import Path

import cmipld.db as db
from cmipld.db.models.mixins import TermKind
from cmipld.db.models.univers import DataDescriptor, UTerm
from cmipld.db import read_json_file
import cmipld.settings as settings

_LOGGER = logging.getLogger("univers_ingestion")


def infer_term_kind(json_specs: dict) -> TermKind:
    if settings.PATTERN_JSON_KEY in json_specs:
        return TermKind.PATTERN
    elif settings.COMPOSITE_JSON_KEY in json_specs:
        return TermKind.COMPOSITE
    else:
        return TermKind.PLAIN


def ingest_data_descriptor(data_descriptor_path: Path,
                           connection: db.DBConnection) -> None:
    context_file_path = data_descriptor_path.joinpath(settings.CONTEXT_FILENAME)
    try:
        context = read_json_file(context_file_path)
    except Exception as e:
        msg = f'Unable to read the context file {context_file_path} of data descriptor \
               {data_descriptor_path.name}. Skip.\n{str(e)}'
        _LOGGER.error(msg)
        return        
    with connection.create_session() as session:
        data_descriptor = DataDescriptor(id=data_descriptor_path.name, context=context)
        session.add(data_descriptor)
        for term_file_path in db.items_of_interest(dir_path=data_descriptor_path,
                                                   glob_inclusion_pattern='*.json',
                                                   exclude_prefixes=settings.SKIPED_FILE_DIR_NAME_PREFIXES,
                                                   kind='file'):
            try:
                json_specs = read_json_file(term_file_path)
                term_id = json_specs[settings.TERM_ID_JSON_KEY]
            except Exception as e:
                _LOGGER.error(f'Unable to read term {term_file_path}. Skip.\n{e}')
                continue
            kind = infer_term_kind(json_specs)
            term = UTerm(
                id=term_id,
                specs=json_specs,
                data_descriptor=data_descriptor,
                kind=kind,
            )
            session.add(term)
        session.commit()


def ingest_univers(univer_dir_path: Path, univers_db_file_path: Path) -> None:
    try:
        connection = db.DBConnection(univers_db_file_path)
    except Exception as e:
        msg = f'Unable to read univers SQLite file at {univers_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise IOError(msg) from e
    try:
        data_descriptor_ids = db.items_of_interest(dir_path=univer_dir_path,
                                                   exclude_prefixes=settings.SKIPED_FILE_DIR_NAME_PREFIXES,
                                                   kind='dir')
    except Exception as e:
        msg = f'Unable to list data descriptor in {univer_dir_path}. Abort.'
        _LOGGER.fatal(msg)
        raise IOError(msg) from e
    for data_descriptor_id in data_descriptor_ids:
        try:
            ingest_data_descriptor(univer_dir_path.joinpath(data_descriptor_id), connection)
        except Exception as e:
            msg = f'Unexpected error while processing data descriptor {data_descriptor_id}. Abort.'
            _LOGGER.fatal(msg)
            raise RuntimeError(msg) from e


if __name__ == "__main__":
    ingest_univers(Path(sys.argv[1]), Path(sys.argv[2]))