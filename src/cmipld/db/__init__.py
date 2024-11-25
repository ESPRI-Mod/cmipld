import json
from pathlib import Path
from typing import Generator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

import cmipld.settings as settings


def read_json_file(json_file_path: Path) -> dict:
    return json.loads(json_file_path.read_text())


# TODO: repositories structures should be reworked.
def items_of_interest(dir_path: Path, kind: str = None) -> Generator[Path]:
    for directory_object in dir_path.iterdir():
        escape_this_item = False
        for escape_char in settings.SKIPED_DIR_ITEMS:
            if directory_object.name.startswith(escape_char):
                escape_this_item = True
                break
        if escape_this_item:
            continue
        else:
            match kind:
                case 'dir':
                    if directory_object.is_dir():
                        yield directory_object
                    else:
                        continue
                case 'file':
                    if directory_object.is_file():
                        yield directory_object
                    else:
                        continue
                case 'all':
                    yield directory_object
                
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