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
    _ENGINES: dict[Path, Engine] = dict()

    def __init__(self, db_file_path: Path, name: str|None = None, echo: bool = False) -> None:
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

    def get_name(self) -> str|None:
        return self.name
    
    def get_file_path(self) -> Path:
        return self.file_path



