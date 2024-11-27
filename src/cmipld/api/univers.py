from pydantic import BaseModel
from sqlmodel import Session, select

import cmipld.db as db
from cmipld import get_pydantic_class
from cmipld.api import SearchSettings, create_str_comparison_expression
from cmipld.db.models.univers import DataDescriptor, UTerm

############## DEBUG ##############
# TODO: to be deleted.
# The following instructions are only temporary as long as a complet data managment will be implmented.
UNIVERS_DB_CONNECTION = db.DBConnection(db.UNIVERS_DB_FILE_PATH, 'univers', False)
###################################


# Settings only apply on the term_id comparison.
def _find_term_in_data_descriptor(data_descriptor_id: str,
                                  term_id: str, settings: SearchSettings,
                                  session: Session) -> list[UTerm]:
    where_expression = create_str_comparison_expression(field=UTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(UTerm).join(DataDescriptor).where(DataDescriptor.id==data_descriptor_id,
                                                         where_expression)
    results = session.exec(statement).all()
    return results


def find_term_in_data_descriptor(data_descriptor_id: str,
                                 term_id: str,
                                 settings: SearchSettings = SearchSettings()) \
                                    -> dict[str: type[BaseModel]]:
    """Finds one or more terms in the given data descriptor.
    It returns an empty dictionary if one of the given ids is not found.
    The result length depends of the search settings that only apply on the term_id.
    This function search exactly for the given data_descriptor_id
    and won't search for close data_descriptor_ids.
    If the search type is EXACT or REGEX, length is 0 or 1, otherwise length >= 0.

    :param data_descriptor_id: A data descriptor id
    :type data_descriptor_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dict[term id: term pydantic instance]
    :rtype: dict[str: type[BaseModel]]
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        result = dict()
        terms = _find_term_in_data_descriptor(data_descriptor_id, term_id, settings, session)
        if terms:
            term_class = get_pydantic_class(data_descriptor_id)
            for term in terms:
                result[term.id] = term_class(**term.specs)
    return result


def _find_terms_in_univers(term_id: str,
                           settings: SearchSettings, session: Session) -> list[UTerm]:
    where_expression = create_str_comparison_expression(field=UTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(UTerm).where(where_expression)
    results = session.exec(statement).all()
    return results


def find_terms_in_univers(term_id: str,
                          settings: SearchSettings = SearchSettings()) \
                            -> dict[str, dict[str, type[BaseModel]]]:
    """Finds one or more terms of the univers.
    It returns an empty dictionary if the given id is not found.
    Terms are unique within a data descriptor but may have some synonyms within the univers.
    The result length depends of the search settings.
    If the search type is EXACT or REGEX, length is 0 or 1 per data descriptor, otherwise length >= 0.

    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dict[data descriptor id, dict[term id, term pydantic instance]]
    :rtype: dict[str, dict[str, type[BaseModel]]]
    """
    result = dict()
    with UNIVERS_DB_CONNECTION.create_session() as session:
        terms = _find_terms_in_univers(term_id, settings, session)
        for term in terms:
            if term.data_descriptor.id not in result:
                result[term.data_descriptor.id] = dict()
            term_class = get_pydantic_class(term.data_descriptor.id)
            result[term.data_descriptor.id][term.id] = term_class(**term.specs)
    return result


def _get_all_terms_in_data_descriptor(data_descriptor: DataDescriptor) -> list[type[BaseModel]]:
    result = list()
    term_class = get_pydantic_class(data_descriptor.id)
    for term in data_descriptor.terms:
        result.append(term_class(**term.specs))
    return result


def _find_data_descriptors_in_univers(data_descriptor_id,
                                      settings, session) -> list[DataDescriptor]:
    where_expression = create_str_comparison_expression(field=DataDescriptor.id,
                                                        value=data_descriptor_id,
                                                        settings=settings)
    statement = select(DataDescriptor).where(where_expression)
    results = session.exec(statement).all()
    return results


def get_all_terms_in_data_descriptor(data_descriptor_id: str,
                                     settings: SearchSettings = SearchSettings()) \
                                        -> dict[str, dict[str, type[BaseModel]]]:
    """Gets all the term of the given data descriptor.
    It returns an empty dictionary if the given id is not found.
    The result length depends of the search settings.
    If the search type is EXACT or REGEX, length is 0 or 1, otherwise length >= 0.

    :param data_descriptor_id: The data descriptor id
    :type data_descriptor_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dict[data descriptor id: [term id: term pydantic instance]]
    :rtype: dict[str, dict[str, type[BaseModel]]]
    """
    result = dict()
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _find_data_descriptors_in_univers(data_descriptor_id,
                                                             settings, session)
        for data_descriptor in data_descriptors:
            result[data_descriptor.id] = dict()
            terms = _get_all_terms_in_data_descriptor(data_descriptor)
            for term in terms:
                result[data_descriptor.id][term.id] = term
    return result


def find_data_descriptors_in_univers(data_descriptor_id: str,
                                     settings: SearchSettings = SearchSettings()) \
                                        -> dict[str, dict]:
    """Finds one or more data descriptor of the univers.
    It returns an empty dictionary if the given id is not found.
    The result length depends of the search settings.
    If the search type is EXACT or REGEX, length is 0 or 1, otherwise length >= 0.

    :param data_descriptor_id: A data descriptor id to be found
    :type data_descriptor_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dict[data descriptor id, data descriptor context]
    :rtype: dict[str, dict]
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _find_data_descriptors_in_univers(data_descriptor_id, settings, session)
        result = dict()
        for data_descriptor in data_descriptors:
            result[data_descriptor.id] = data_descriptor.context
    return result


def _get_all_data_descriptors_in_univers(session: Session) -> list[DataDescriptor]:
    statement = select(DataDescriptor)
    data_descriptors = session.exec(statement)
    result = data_descriptors.all()
    return result


def get_all_data_descriptors_in_univers() -> dict[str, dict]:
    """Gets all the data descriptors of the univers

    :returns: A dict[data descriptor id, data descriptor context]
    :rtype: dict[str, dict]
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _get_all_data_descriptors_in_univers(session)
        result = dict()
        for data_descriptor in data_descriptors:
            result[data_descriptor.id] = data_descriptor.context
    return result


def get_all_terms_in_univers() -> dict[str, dict[str, type[BaseModel]]]:
    """Gets all the terms of the univers

    :returns: A dict[data descriptor id, dict[term id, term pydantic instance]]
    :rtype: dict[str, dict[str, type[BaseModel]]]
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _get_all_data_descriptors_in_univers(session)
        result = dict()
        for data_descriptor in data_descriptors:
            # Term may have some sysnonyms within the whole univers.
            result[data_descriptor.id] = dict()
            terms = _get_all_terms_in_data_descriptor(data_descriptor)
            for term in terms:
                result[data_descriptor.id][term.id] = term
    return result


if __name__ == "__main__":
    find_term_in_data_descriptor('institution', 'ipsl')