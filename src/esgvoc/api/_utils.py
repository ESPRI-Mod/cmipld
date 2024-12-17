from typing import Sequence

import esgvoc.core.service as service
import esgvoc.core.constants as api_settings
from esgvoc.api.data_descriptors import DATA_DESCRIPTOR_CLASS_MAPPING
from esgvoc.api.search import SearchSettings, SearchType
from esgvoc.core.db.models.project import PTerm
from esgvoc.core.db.models.universe import UTerm
from pydantic import BaseModel
from sqlalchemy import ColumnElement, func
from sqlmodel import Session, col

UNIVERSE_DB_CONNECTION = service.state_service.universe.db_connection


def get_pydantic_class(data_descriptor_id_or_term_type: str) -> type[BaseModel]:
    if data_descriptor_id_or_term_type in DATA_DESCRIPTOR_CLASS_MAPPING:
        return DATA_DESCRIPTOR_CLASS_MAPPING[data_descriptor_id_or_term_type]
    else:
        raise ValueError(f"{data_descriptor_id_or_term_type} pydantic class not found")


def get_universe_session() -> Session:
    if UNIVERSE_DB_CONNECTION:
        return UNIVERSE_DB_CONNECTION.create_session()
    else:
        raise RuntimeError('universe connection is not initialized')


def instantiate_pydantic_term(term: UTerm|PTerm) -> BaseModel:
    term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
    return term_class(**term.specs)


def instantiate_pydantic_terms(db_terms: Sequence[UTerm|PTerm],
                               list_to_populate: list[BaseModel]) -> None:
    for db_term in db_terms:
        term = instantiate_pydantic_term(db_term)
        list_to_populate.append(term)


def create_str_comparison_expression(field: str,
                                     value: str,
                                     settings: SearchSettings|None) -> ColumnElement:
    '''
    SQLite LIKE is case insensitive (and so STARTS/ENDS_WITH which are implemented with LIKE).
    So the case sensitive LIKE is implemented with REGEX.
    The i versions of SQLAlchemy operators (icontains, etc.) are not useful
    (but other dbs than SQLite should use them).
    If the provided `settings` is None, this functions returns an exact search expression.
    '''
    does_wild_cards_in_value_have_to_be_interpreted = False
    # Shortcut.
    if settings is None:
        return col(field).is_(other=value)
    else:
        match settings.type:
            # Early return because not operator is not implement with tilde symbol.
            case SearchType.EXACT:
                if settings.case_sensitive:
                    if settings.not_operator:
                        return col(field).is_not(other=value)
                    else:
                        return col(field).is_(other=value)
                else:
                    if settings.not_operator:
                        return func.lower(field) != func.lower(value)
                    else:
                        return func.lower(field) == func.lower(value)
            case SearchType.LIKE:
                if settings.case_sensitive:
                    result = col(field).regexp_match(pattern=f".*{value}.*")
                else:
                    result = col(field).contains(
                        other=value,
                        autoescape=not does_wild_cards_in_value_have_to_be_interpreted,
                    )
            case SearchType.STARTS_WITH:
                if settings.case_sensitive:
                    result = col(field).regexp_match(pattern=f"^{value}.*")
                else:
                    result = col(field).startswith(
                        other=value,
                        autoescape=not does_wild_cards_in_value_have_to_be_interpreted,
                    )
            case SearchType.ENDS_WITH:
                if settings.case_sensitive:
                    result = col(field).regexp_match(pattern=f"{value}$")
                else:
                    result = col(field).endswith(
                        other=value,
                        autoescape=not does_wild_cards_in_value_have_to_be_interpreted,
                    )
            case SearchType.REGEX:
                if settings.case_sensitive:
                    result = col(field).regexp_match(pattern=value)
                else:
                    raise NotImplementedError(
                        "regex string comparison case insensitive is not implemented"
                    )
        if settings.not_operator:
            return ~result
        else:
            return result