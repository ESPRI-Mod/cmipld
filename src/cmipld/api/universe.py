from pydantic import BaseModel
from sqlmodel import Session, select

import cmipld.db as db
from cmipld import get_pydantic_class
from cmipld.api import SearchSettings, create_str_comparison_expression, SearchType
from cmipld.db.models.univers import DataDescriptor, UTerm
import cmipld.settings as api_settings

############## DEBUG ##############
# TODO: to be deleted.
# The following instructions are only temporary as long as a complet data managment will be implmented.
UNIVERS_DB_CONNECTION = db.DBConnection(db.UNIVERS_DB_FILE_PATH, 'univers', False)
###################################


def _find_terms_in_data_descriptor(data_descriptor_id: str,
                                   term_id: str,
                                   session: Session,
                                   settings: SearchSettings|None) -> UTerm|list[UTerm]|None:
    """Settings only apply on the term_id comparison."""
    where_expression = create_str_comparison_expression(field=UTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(UTerm).join(DataDescriptor).where(DataDescriptor.id==data_descriptor_id,
                                                         where_expression)
    results = session.exec(statement)
    if settings is None or SearchType.EXACT == settings.type:
        # As we compare id, it can't be more than one result.
        result = results.one_or_none()
    else:
        result = results.all()
    return result


def find_terms_in_data_descriptor(data_descriptor_id: str,
                                  term_id: str,
                                  settings: SearchSettings|None = None) \
                                     -> BaseModel|dict[str: BaseModel]|None:
    """
    Finds one or more terms in the given data descriptor based on the specified search settings.
    This function performs an exact match on the `data_descriptor_id` and does **not** search for similar or related descriptors.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    If any of the provided ids (`data_descriptor_id` or `term_id`) is not found, the function returns `None`.

    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns `None` or a Pydantic model term instance.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns `None` or a dictionary that maps term ids found
    to their corresponding Pydantic model instances.

    :param data_descriptor_id: A data descriptor id
    :type data_descriptor_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: a Pydantic model term instance or a dictionary that maps term ids found to their corresponding Pydantic model instances.
    Returns `None` if no matches are found.
    :rtype: BaseModel|dict[str: BaseModel]|None
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        result = None
        terms = _find_terms_in_data_descriptor(data_descriptor_id, term_id, session, settings)
        if terms:
            if settings is None or SearchType.EXACT == settings.type:
                term_class = get_pydantic_class(terms.specs[api_settings.TERM_TYPE_JSON_KEY])
                result = term_class(**terms.specs)
            else:
                result = dict()
                for term in terms:
                    term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
                    result[term.id] = term_class(**term.specs)
    return result


def _find_terms_in_univers(term_id: str,
                           session: Session,
                           settings: SearchSettings|None) -> list[UTerm]:
    where_expression = create_str_comparison_expression(field=UTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(UTerm).where(where_expression)
    results = session.exec(statement).all()
    return results


def find_terms_in_univers(term_id: str,
                          settings: SearchSettings|None = None) \
                            -> dict[str, BaseModel]|\
                               dict[str, dict[str, BaseModel]]|\
                               None:
    """
    Finds one or more terms of the univers.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    As terms are unique within a data descriptor but may have some synonyms within the univers,
    the result maps every term found to their data descriptor.
    If the provided `term_id` is not found, the function returns `None`.

    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns `None` or a dictionary that maps
      data descriptor ids to a Pydantic model term instance.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns `None` or a dictionary that maps
      data descriptor ids to a mapping of term ids and their corresponding Pydantic model instances.

    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A dictionary that maps data descriptor ids to a Pydantic model term instance
    or a dictionary that maps data descriptor ids
    to a mapping of term ids and their corresponding Pydantic model instances.
    Returns `None` if no matches are found.
    :rtype: dict[str, BaseModel]|dict[str, dict[str, BaseModel]]|None
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        terms = _find_terms_in_univers(term_id, session, settings)
        if terms:
            result = dict()
            for term in terms:
                term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
                if settings is None or SearchType.EXACT == settings.type:
                    result[term.data_descriptor.id] = term_class(**term.specs)
                else:
                    if term.data_descriptor.id not in result:
                        result[term.data_descriptor.id] = dict()
                    result[term.data_descriptor.id][term.id] = term_class(**term.specs)
        else:
            result = None
    return result


def _get_all_terms_in_data_descriptor(data_descriptor: DataDescriptor) -> list[BaseModel]:
    result = list()
    for term in data_descriptor.terms:
        term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
        result.append(term_class(**term.specs))
    return result


def _find_data_descriptors_in_univers(data_descriptor_id: str,
                                      session: Session,
                                      settings: SearchSettings|None) -> DataDescriptor|list[DataDescriptor]|None:
    where_expression = create_str_comparison_expression(field=DataDescriptor.id,
                                                        value=data_descriptor_id,
                                                        settings=settings)
    statement = select(DataDescriptor).where(where_expression)
    results = session.exec(statement)
    if settings is None or SearchType.EXACT == settings.type:
        # As we compare id, it can't be more than one result.
        result = results.one_or_none()
    else:
        result = results.all()
    return result


def get_all_terms_in_data_descriptor(data_descriptor_id: str) \
                                        -> dict[str, BaseModel]|None:
    """
    Gets all the terms of the given data descriptor.
    This function performs an exact match on the `data_descriptor_id` and does **not** search for similar or related descriptors.
    As a result, the function returns a dictionary that maps term ids to their corresponding Pydantic instances.
    If the provided `data_descriptor_id` is not found, the function returns `None`.

    :param data_descriptor_id: A data descriptor id
    :type data_descriptor_id: str
    :returns: a dictionary that maps term ids to their corresponding Pydantic instances.
    Returns `None` if no matches are found.
    :rtype: dict[str, BaseModel]|None
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptor = _find_data_descriptors_in_univers(data_descriptor_id,
                                                            session,
                                                            None)
        if data_descriptor:
            result = dict()
            terms = _get_all_terms_in_data_descriptor(data_descriptor)
            for term in terms:
                result[term.id] = term
        else:
            result = None
    return result


def find_data_descriptors_in_univers(data_descriptor_id: str,
                                     settings: SearchSettings|None = None) \
                                        -> dict|dict[str, dict]|None:
    """
    Finds one or more data descriptor of the univers, based on the specified search settings.
    The given `data_descriptor_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `data_descriptor_id`.
    If the provided `data_descriptor_id` is not found, the function returns `None`.
    
    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns `None` or a data descriptor context.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns `None` or 
      dictionary that maps data descriptor ids to their context.

    :param data_descriptor_id: A data descriptor id to be found
    :type data_descriptor_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A data descriptor context or dictionary that maps data descriptor ids to their context.
    Returns `None` if no matches are found.
    :rtype: dict|dict[str, dict]|None
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _find_data_descriptors_in_univers(data_descriptor_id,
                                                             session,
                                                             settings)
        if data_descriptors:
            if settings is None or SearchType.EXACT == settings.type:
                result = data_descriptors.context
            else:
                result = dict()
                for data_descriptor in data_descriptors:
                    result[data_descriptor.id] = data_descriptor.context
        else:
            result = None
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


def get_all_terms_in_univers() -> dict[str, dict[str, BaseModel]]:
    """
    Gets all the terms of the univers.
    As terms are unique within a data descriptor but may have some synonyms within the univers,
    the result maps every term to their data descriptor.

    :returns: A dictionary that maps data descriptor ids to a mapping of term ids and their corresponding Pydantic model instances.
    :rtype: dict[str, dict[str, BaseModel]]
    """
    with UNIVERS_DB_CONNECTION.create_session() as session:
        data_descriptors = _get_all_data_descriptors_in_univers(session)
        result = dict()
        for data_descriptor in data_descriptors:
            # Term may have some synonyms within the whole univers.
            result[data_descriptor.id] = dict()
            terms = _get_all_terms_in_data_descriptor(data_descriptor)
            for term in terms:
                result[data_descriptor.id][term.id] = term
    return result


if __name__ == "__main__":
    print(find_terms_in_univers('ipsl'))