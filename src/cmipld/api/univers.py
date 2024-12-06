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
    """
    Finds one or more terms in the given data descriptor based on the specified search settings.
    This function performs an exact match on the `data_descriptor_id` and does **not** search for similar or related descriptors.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE`, `STARTS_WITH` and `ENDS_WITH` may return multiple results).
    As a result, the function returns a dictionary that mapps term ids found to their corresponding Pydantic model instances.
    If any of the provided IDs (`data_descriptor_id` or `term_id`) is not found, the function returns an empty dictionary.

    Behavior based on search type:
    - `EXACT` or `REGEX`: returns 0 or 1 result.
    - `LIKE`, `STARTS_WITH` and `ENDS_WITH`: may return multiple results.

    :param data_descriptor_id: A data descriptor id
    :type data_descriptor_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dictionary that mapps term IDs found to their corresponding Pydantic model instances.
    Returns an empty dictionary if no matches are found.
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
    """
    Finds one or more terms of the univers.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE`, `STARTS_WITH` and `ENDS_WITH` may return multiple results).
    As terms are unique within a data descriptor but may have some synonyms within the univers,
    the result maps every term found to their data descriptor.
    If the provided `term_id` is not found, the function returns an empty dictionary.

    Behavior based on search type:
    - `EXACT` or `REGEX`: returns 0 or 1 result per data descriptor.
    - `LIKE`, `STARTS_WITH` and `ENDS_WITH`: may return multiple results per data descriptor.

    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dictionary that maps data descriptor ids to a mapping of term ids and their corresponding Pydantic model instances.
    Returns an empty dictionary if no matches are found.
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


def get_all_terms_in_data_descriptor(data_descriptor_id: str) \
                                        -> dict[str, type[BaseModel]]:
    """
    Gets all the terms of the given data descriptor.
    This function performs an exact match on the `data_descriptor_id` and does **not** search for similar or related descriptors.
    As a result, the function returns a dictionary that maps term ids to their corresponding Pydantic instances.
    If the provided `data_descriptor_id` is not found, the function returns an empty dictionary.

    :param data_descriptor_id: The data descriptor id
    :type data_descriptor_id: str
    :returns: a dictionary that maps term ids to their corresponding Pydantic instances.
    Returns an empty dictionary if no matches are found.
    :rtype: dict[str, type[BaseModel]]
    """
    result = dict()
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _find_data_descriptors_in_univers(data_descriptor_id,
                                                             SearchSettings(),
                                                             session)
        if data_descriptors:
            data_descriptor = data_descriptors[0]
            terms = _get_all_terms_in_data_descriptor(data_descriptor)
            for term in terms:
                result[term.id] = term
    return result


def find_data_descriptors_in_univers(data_descriptor_id: str,
                                     settings: SearchSettings = SearchSettings()) \
                                        -> dict[str, dict]:
    """
    Finds one or more data descriptor of the univers.
    The given `data_descriptor_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE`, `STARTS_WITH` and `ENDS_WITH` may return multiple results).
    As a result, the function returns a dictionary that maps data descriptor ids to their context.
    If the provided `data_descriptor_id` is not found, the function returns an empty dictionary.
    
    Behavior based on search type:
    - `EXACT` or `REGEX`: returns 0 or 1 result.
    - `LIKE`, `STARTS_WITH` and `ENDS_WITH`: may return multiple results.

    :param data_descriptor_id: A data descriptor id to be found
    :type data_descriptor_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dictionary that maps data descriptor ids to their context.
    Returns an empty dictionary if no matches are found.
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
    """
    Gets all the data descriptors of the univers.

    :returns: A dictionary that maps data descriptor ids to their context.
    :rtype: dict[str, dict]
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _get_all_data_descriptors_in_univers(session)
        result = dict()
        for data_descriptor in data_descriptors:
            result[data_descriptor.id] = data_descriptor.context
    return result


def get_all_terms_in_univers() -> dict[str, dict[str, type[BaseModel]]]:
    """
    Gets all the terms of the univers.
    As terms are unique within a data descriptor but may have some synonyms within the univers,
    the result maps every term to their data descriptor.

    :returns: A dictionary that maps data descriptor ids to a mapping of term ids and their corresponding Pydantic model instances.
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
    get_all_terms_in_data_descriptor('institution')