from sqlalchemy import Engine
from sqlmodel import Session, create_engine


# Singleton for SQLModel engines.
# Not thread safe.
class DBConnection:
    SQLITE_URL_PREFIX = 'sqlite://'
    _ENGINES: dict[str, Engine] = dict()

    def __init__(self, db_filename: str, name: str, echo: bool = False) -> None:
        if db_filename in DBConnection._ENGINES:
            raise ValueError(f"{db_filename} is already connected")
        else:
            self.engine = create_engine(f'{DBConnection.SQLITE_URL_PREFIX}/{db_filename}', echo=echo)
            self.name = name
            self.filename = db_filename
            DBConnection._ENGINES[db_filename] = self.engine

    def set_echo(self, echo: bool) -> None:
        self.engine.echo = echo

    def get_engine(self) -> Engine:
        return self.engine

    def create_session(self) -> Session:
        return Session(self.engine)

    def get_name(self) -> str:
        return self.name
    
    def get_file_name(self) -> str:
        return self.filename


############## DEBUG ##############
# The following instructions are only temporary as long as a complet data managment will be implmented.

UNIVERS_DB_CONNECTION = DBConnection('univers.sqlite', 'univers', False)
CMIP6PLUS_DB_CONNECTION = DBConnection('projects.sqlite', 'cmip6plus', False)

###################################
