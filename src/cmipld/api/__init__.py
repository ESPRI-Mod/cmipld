from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Sequence
from dataclasses import dataclass

from pydantic import BaseModel
from sqlalchemy import ColumnElement, func
from sqlmodel import col

import cmipld.settings as api_settings
from cmipld.api.data_descriptors import get_pydantic_class
from cmipld.db.models.mixins import TermKind
from cmipld.db.models.project import PTerm
from cmipld.db.models.universe import UTerm


def instantiate_pydantic_term(term: UTerm|PTerm) -> BaseModel:
    term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
    return term_class(**term.specs)


def instantiate_pydantic_terms(db_terms: Sequence[UTerm|PTerm],
                               list_to_populate: list[BaseModel]) -> None:
    for db_term in db_terms:
        term = instantiate_pydantic_term(db_term)
        list_to_populate.append(term)


class ValidationErrorVisitor(ABC):
    @abstractmethod
    def visit_universe_term_error(self, error: "UniverseTermError") -> Any:
        pass

    @abstractmethod
    def visit_project_term_error(self, error: "ProjectTermError") -> Any:
        pass


class BasicValidationErrorVisitor(ValidationErrorVisitor):
    def visit_universe_term_error(self, error: "UniverseTermError") -> Any:
        term_id = error.term[api_settings.TERM_ID_JSON_KEY]
        result = f"The term {term_id} from the data descriptor {error.data_descriptor_id} "+\
                 f"does not validate the given value '{error.value}'"
        return result

    def visit_project_term_error(self, error: "ProjectTermError") -> Any:
        term_id = error.term[api_settings.TERM_ID_JSON_KEY]
        result = f"The term {term_id} from the collection {error.collection_id} "+\
                 f"does not validate the given value '{error.value}'"
        return result


class ValidationError(ABC):
    def __init__(self,
                 value: str):
        self.value: str = value
    
    @abstractmethod
    def accept(self, visitor: ValidationErrorVisitor) -> Any:
        pass

class UniverseTermError(ValidationError):
    def __init__(self,
                 value: str,
                 term: UTerm):
        super().__init__(value)
        self.term: dict = term.specs
        self.term_kind: TermKind = term.kind
        self.data_descriptor_id: str = term.data_descriptor.id

    def accept(self, visitor: ValidationErrorVisitor) -> Any:
        return visitor.visit_universe_term_error(self)


class ProjectTermError(ValidationError):
    def __init__(self,
                 value: str,
                 term: PTerm):
        super().__init__(value)
        self.term: dict = term.specs
        self.term_kind: TermKind = term.kind
        self.collection_id: str = term.collection.id

    def accept(self, visitor: ValidationErrorVisitor) -> Any:
        return visitor.visit_project_term_error(self)


class ValidationReport:
    def __init__(self,
                 given_expression: str,
                 errors: list[ValidationError]):
        self.expression: str = given_expression
        self.errors: list[ValidationError] = errors
        self.nb_errors = len(self.errors) if self.errors else 0
        self.validated: bool = False if errors else True
        self.message = f"'{self.expression}' has {self.nb_errors} error(s)"
   
    def __len__(self) -> int:
        return self.nb_errors
    
    def __bool__(self) -> bool:
        return self.validated
    
    def __repr__(self) -> str:
        return self.message


@dataclass
class MatchingTerm:
    project_id: str
    collection_id: str
    term_id: str


class SearchType(Enum):
    EXACT = ("exact",)
    LIKE = ("like",)  # can interpret %
    STARTS_WITH = ("starts_with",)  # can interpret %
    ENDS_WITH = "ends_with"  # can interpret %
    REGEX = ("regex",)


class SearchSettings(BaseModel):
    type: SearchType = SearchType.EXACT
    case_sensitive: bool = True
    not_operator: bool = False


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
