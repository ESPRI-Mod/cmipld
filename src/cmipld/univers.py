from pydantic import BaseModel

from sqlmodel import select, Session

import cmipld.db as db
import cmipld.utils.functions as functions
from cmipld.models.sqlmodel.univers import UTerm, DataDescriptor


def _get_all_data_descriptors(session: Session) -> list[DataDescriptor]:
    statement = select(DataDescriptor)
    data_descriptors = session.exec(statement)
    result = data_descriptors.all()
    return result


def _get_data_descriptor(data_descriptor_id: str, session: Session) -> DataDescriptor:
    statement = select(DataDescriptor).where(DataDescriptor.id==data_descriptor_id)
    results = session.exec(statement)
    result = results.one()
    return result


def _get_terms(data_descriptor: DataDescriptor) -> list[type[BaseModel]]:
    result = list()
    term_class = functions.get_pydantic_class(data_descriptor.id)
    for term in data_descriptor.terms:
        result.append(term_class(**term.specs))
    return result


def _get_term(data_descriptor_id: str, term_id: str, session: Session) -> UTerm:
    statement = select(UTerm).join(DataDescriptor).where(DataDescriptor.id==data_descriptor_id,
                                                         UTerm.id==term_id)
    results = session.exec(statement)
    result = results.one()
    return result


def get_term(data_descriptor_id: str, term_id: str) -> type[BaseModel]:
    with db.UNIVERS_DB_CONNECTION.create_session() as session:
        term = _get_term(data_descriptor_id, term_id, session)
        term_class = functions.get_pydantic_class(data_descriptor_id)
        return term_class(**term.specs)


def get_terms(data_descriptor_id: str) -> dict[str, type[BaseModel]]:
    with db.UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptor = _get_data_descriptor(data_descriptor_id, session)
        terms = _get_terms(data_descriptor)
        result = dict()
        for term in terms:
            result[term.id] = term
        return result


def get_all_data_descriptors() -> dict[str, dict]:
    with db.UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _get_all_data_descriptors(session)
        result = dict()
        for data_descriptor in data_descriptors:
            result[data_descriptor.id] = data_descriptor.context
    return result


def get_all_terms() -> dict[str, type[BaseModel]]:
    with db.UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _get_all_data_descriptors(session)
        result = dict()
        for data_descriptor in data_descriptors:
            terms = _get_terms(data_descriptor)
            for term in terms:
                result[term.id] = term
    return result