import logging
from pathlib import Path

from cmipld.core.data_handler import JsonLdResource
from cmipld.core.service.data_merger import DataMerger
from sqlmodel import Session, select

import cmipld.db as db
import cmipld.settings as settings
from cmipld.db import read_json_file
from cmipld.db.models.mixins import TermKind
from cmipld.db.models.univers import DataDescriptor, UTerm, Univers
from cmipld.db.models.univers import univers_create_db

_LOGGER = logging.getLogger(__name__)

def infer_term_kind(json_specs: dict) -> TermKind:
    if settings.PATTERN_JSON_KEY in json_specs:
        return TermKind.PATTERN
    elif settings.COMPOSITE_JSON_KEY in json_specs:
        return TermKind.COMPOSITE
    else:
        return TermKind.PLAIN


def ingest_univers(universe_repo_dir_path: Path, univers_db_file_path: Path) -> None:
    try:
        connection = db.DBConnection(univers_db_file_path)
    except Exception as e:
        msg = f'Unable to read univers SQLite file at {univers_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise IOError(msg) from e

    for data_descriptor_dir_path in universe_repo_dir_path.iterdir(): 
        if data_descriptor_dir_path.is_dir() and (data_descriptor_dir_path / "000_context.jsonld").exists(): # TOOD maybe put that in setting  
            try:
                ingest_data_descriptor(data_descriptor_dir_path, connection)
            except Exception as e:
                msg = f'Unexpected error while processing data descriptor {data_descriptor_dir_path}. Abort.'
                _LOGGER.fatal(msg)
                raise RuntimeError(msg) from e
        
def ingest_metadata_universe(connection,git_hash):
    with connection.create_session() as session:
        universe = Univers(git_hash=git_hash)
        session.add(universe)    
        session.commit()

def ingest_data_descriptor(data_descriptor_path: Path,
                           connection: db.DBConnection) -> None:


    data_descriptor_id = data_descriptor_path.name

    context_file_path = data_descriptor_path.joinpath(settings.CONTEXT_FILENAME)
    try:
        context = read_json_file(context_file_path)
    except Exception as e:
        msg = f'Unable to read the context file {context_file_path} of data descriptor \
               {data_descriptor_id}. Skip.\n{str(e)}'
        _LOGGER.warning(msg)
        return        


    with connection.create_session() as session:
        data_descriptor = DataDescriptor(id=data_descriptor_id, context=context, term_kind=TermKind.PLAIN)
        session.add(data_descriptor)
        _LOGGER.debug(f"add data_descriptor : {data_descriptor_id}")
        for term_file_path in data_descriptor_path.iterdir():
            _LOGGER.debug(f"found term path : {term_file_path} , {term_file_path.suffix}")
            if term_file_path.is_file() and term_file_path.suffix == ".json":
                try:
                    json_specs=DataMerger(data=JsonLdResource(uri=str(term_file_path)),
                                          locally_available={"https://espri-mod.github.io/mip-cmor-tables":".cache/repos/mip-cmor-tables"}).merge_linked_json()[-1]
                    term_kind = infer_term_kind(json_specs)
                    term_id = json_specs["id"]

                except Exception as e:
                    _LOGGER.warning(f'Unable to read term {term_file_path}. Skip.\n{str(e)}')
                    continue
                if term_id and json_specs and data_descriptor and term_kind:
                    _LOGGER.debug("adding {term_id}")
                    term = UTerm(
                        id=term_id,
                        specs=json_specs,
                        data_descriptor=data_descriptor,
                        kind=term_kind,
                    )
                    session.add(term)
        session.commit()

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


if __name__ == "__main__":
    #ingest_univers(db.UNIVERS_DIR_PATH, db.UNIVERS_DB_FILE_PATH)
    import os
    root_dir = Path(str(os.getcwd())).parent.parent
    print(root_dir)
    univers_create_db(root_dir /  Path(".cache/dbs/univers.sqlite"))
    ingest_univers(root_dir / Path(".cache/repos/mip-cmor-tables"),root_dir /  Path(".cache/dbs/univers.sqlite"))
