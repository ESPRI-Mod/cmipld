from sqlmodel import Field
from enum import Enum


class TermKind(Enum):
    PLAIN = 'plain'
    PATTERN = 'pattern'
    COMPOSITE = 'composite'


class PkMixin:
    pk: int | None = Field(default=None, primary_key=True)


class IdMixin:
    id: str = Field(index=True)