import json
from pathlib import Path

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

def read_json_file(json_file_path: Path) -> dict:
    return json.loads(json_file_path.read_text())

# Singleton for SQLModel engines.
# Not thread safe.
class DBConnection:
    SQLITE_URL_PREFIX = 'sqlite://'
    _ENGINES: dict[str, Engine] = dict()

    def __init__(self, db_file_path: Path, echo: bool = False) -> None:
        absolute_str_path = str(db_file_path.absolute())
        if absolute_str_path in DBConnection._ENGINES:
            self.engine = DBConnection._ENGINES[absolute_str_path]
        else:
            self.engine = create_engine(f'{DBConnection.SQLITE_URL_PREFIX}/{absolute_str_path}', echo=echo)
            DBConnection._ENGINES[absolute_str_path] = self.engine
        self.name = db_file_path.stem
        self.file_path = db_file_path.absolute()

    def set_echo(self, echo: bool) -> None:
        self.engine.echo = echo

    def get_engine(self) -> Engine:
        return self.engine

    def create_session(self) -> Session:
        return Session(self.engine)

    def get_name(self) -> str|None:
        return self.name
    
    def get_file_path(self) -> Path:
        return self.file_path