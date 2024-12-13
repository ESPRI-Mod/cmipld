from typing import Protocol

class Term(Protocol):
    @property
    def id(self) -> str:
        pass
    @property
    def type(self) -> str:
        pass


class PlainTerm(Term, Protocol):
    @property
    def drs_name(self) -> str:
        pass
    

class TermPattern(Term, Protocol):
    @property
    def regex(self) -> str:
        pass


class CompositePart(Protocol):
    @property
    def id(self) -> str:
        pass
    @property
    def type(self) -> str:
        pass
    @property
    def is_required(self) -> bool:
        pass


class TermComposite(Term, Protocol):
    @property
    def separator(self) -> str:
        pass
    @property
    def parts(self) -> list[CompositePart]:
        pass