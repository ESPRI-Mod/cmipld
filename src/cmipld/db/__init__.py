import json
from pathlib import Path
from typing import Generator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

def read_json_file(json_file_path: Path) -> dict:
    return json.loads(json_file_path.read_text())


# TODO: repositories structures should be reworked.
def items_of_interest(dir_path: Path,
                      glob_inclusion_pattern: str = '*',
                      exclude_prefixes: list[str] = [],
                      kind: str = 'all') -> Generator[Path]:
    for item in dir_path.glob(glob_inclusion_pattern):
        skip_item = False
        for exclude_prefix in exclude_prefixes:
            if item.name.startswith(exclude_prefix):
                skip_item = True
                break
        if skip_item:
            continue
        else:
            match kind:
                case 'dir':
                    if item.is_dir():
                        yield item
                    else:
                        continue
                case 'file':
                    if item.is_file():
                        yield item
                    else:
                        continue
                case 'all':
                    yield item
                case _:
                    raise NotImplementedError(f'kind {kind} is not supported')
                

# Singleton for SQLModel engines.
# Not thread safe.
class DBConnection:
    SQLITE_URL_PREFIX = 'sqlite://'
    _ENGINES: dict[str, Engine] = dict()

    def __init__(self, db_file_path: Path, name: str = None, echo: bool = False) -> None:
        if db_file_path in DBConnection._ENGINES:
            self.engine = DBConnection._ENGINES[db_file_path]
        else:
            self.engine = create_engine(f'{DBConnection.SQLITE_URL_PREFIX}/{str(db_file_path)}', echo=echo)
            DBConnection._ENGINES[db_file_path] = self.engine
        self.name = name
        self.file_path = db_file_path

    def set_echo(self, echo: bool) -> None:
        self.engine.echo = echo

    def get_engine(self) -> Engine:
        return self.engine

    def create_session(self) -> Session:
        return Session(self.engine)

    def get_name(self) -> str:
        return self.name
    
    def get_file_path(self) -> str:
        return self.file_path


############## DEBUG ##############
# TODO: to be deleted.
# The following instructions are only temporary as long as a complet data managment will be implmented.

from cmipld.settings import ROOT_DIR_PATH # noqa

UNIVERS_DIR_NAME = 'mip-cmor-tables'
CMIP6PLUS_DIR_NAME = 'CMIP6Plus_CVs'

UNIVERS_DIR_PATH = ROOT_DIR_PATH.parent.joinpath(UNIVERS_DIR_NAME)
CMIP6PLUS_DIR_PATH = ROOT_DIR_PATH.parent.joinpath(CMIP6PLUS_DIR_NAME)

UNIVERS_DB_FILE_PATH = Path('univers.sqlite')
CMIP6PLUS_DB_FILE_PATH = Path('projects.sqlite')
###################################