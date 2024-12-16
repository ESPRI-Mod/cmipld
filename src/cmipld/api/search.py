from pydantic import BaseModel
from enum import Enum
from dataclasses import dataclass

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