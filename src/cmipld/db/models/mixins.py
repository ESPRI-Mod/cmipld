from enum import Enum

from sqlmodel import Field


class TermKind(Enum):
    PLAIN = "plain"
    PATTERN = "pattern"
    COMPOSITE = "composite"
    MIXED = 'mixed'


class PkMixin:
    pk: int | None = Field(default=None, primary_key=True)


class IdMixin:
    id: str = Field(index=True)
