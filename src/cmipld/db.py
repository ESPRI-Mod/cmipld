from sqlalchemy import Engine
from sqlmodel import Session, create_engine


# Singleton for SQLModel engines.
# Not thread safe.
class DBConnection:

    _engines: dict[str, Engine] = dict()

    def __init__(self, project_sqlite_url: str, name: str, echo: bool = False) -> None:
        if project_sqlite_url in DBConnection._engines:
            raise ValueError(f"{project_sqlite_url} is already connected")
        else:
            self.engine = create_engine(project_sqlite_url, echo=echo)
            self.name = name
            DBConnection._engines[project_sqlite_url] = self.engine

    def set_echo(self, echo: bool) -> None:
        self.engine.echo = echo

    def get_engine(self) -> Engine:
        return self.engine

    def create_session(self) -> Session:
        return Session(self.engine)

    def get_name(self) -> str:
        return self.name


############## DEBUG ##############
# The following instructions are only temporary as long as a complet data managment will be implmented.

UNIVERS_DB_CONNECTION = DBConnection("sqlite:///univers.sqlite", "univers", False)
CMIP6PLUS_DB_CONNECTION = DBConnection("sqlite:///projects.sqlite", "cmip6plus", False)

###################################
