from sqlmodel import Engine, create_engine

import cmipld.utils.settings as settings


# Singleton univers engine.
# Not thread safe.
class UniversEngine:
    _engine = None
    
    def __init__(self) -> None:
        raise NotImplementedError('UniversEngine is a pure static class')

    def get_engine(echo: bool = False) -> Engine:
        if UniversEngine._engine is None:
            UniversEngine._engine = create_engine(settings.UNIVERS_SQLITE_UR, echo=echo)
        UniversEngine._engine.echo = echo
        return UniversEngine._engine


# Singleton project engines.
# Not thread safe.
class ProjectEngine:
    
    _engines_url_short_name_mapping: dict[str, str] = dict()
    _engine_from_short_names: dict[str, Engine] = dict()

    def __init__(self) -> None:
        raise NotImplementedError('ProjectEngine is a pure static class')
    
    @staticmethod
    def create_engine(project_sqlite_url: str, short_name: str, echo: bool = False) -> Engine:
        if project_sqlite_url in ProjectEngine._engines_url_short_name_mapping:
            result = ProjectEngine._engine_from_short_names[ProjectEngine._engines_url_short_name_mapping[project_sqlite_url]]
            result.echo = echo
            ProjectEngine._engine_from_short_names[short_name] = result # Create an alias.
        else:
            result = create_engine(project_sqlite_url, echo=echo)
            ProjectEngine._engines[short_name] = result
            ProjectEngine._engines_url_short_name_mapping[project_sqlite_url] = short_name
        return result
    
    @staticmethod
    def get_engine(short_name: str, echo: bool = False) -> Engine:
        if short_name in ProjectEngine._engine_from_short_names:
            result = ProjectEngine._engine_from_short_names[short_name]
            result.echo = echo
            return result
        else:
            raise ValueError(f'engine for {short_name} is not created yet. You must create the engine before')