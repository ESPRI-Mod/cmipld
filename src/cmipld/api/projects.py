import re
from typing import Sequence

from pydantic import BaseModel
from sqlmodel import Session, and_, select

import cmipld.api.universe as universe
import cmipld.db as db
import cmipld.settings as api_settings
from cmipld.api import (MatchingTerm, ProjectTermError, SearchSettings,
                        UniverseTermError, ValidationError, ValidationReport,
                        create_str_comparison_expression,
                        instantiate_pydantic_term,
                        instantiate_pydantic_terms)
from cmipld.db.models.mixins import TermKind
from cmipld.db.models.project import Collection, Project, PTerm
from cmipld.db.models.universe import UTerm

############## DEBUG ##############
# TODO: to be deleted.
# The following instructions are only temporary as long as a complete data management will be implemented.
UNIVERSE_DB_CONNECTION = db.DBConnection(db.UNIVERSE_DB_FILE_PATH, 'universe', False)
###################################


def _get_project_connection(project_id: str) -> db.DBConnection|None:
    ############## DEBUG ##############
    # TODO: to be deleted.
    # The following instructions are only temporary as long as a complete data management will be implemented.
    return db.DBConnection(db.CMIP6PLUS_DB_FILE_PATH, 'cmip6plus', False)
    ###################################


def _get_project_session_with_exception(project_id: str) -> Session:
    if connection:=_get_project_connection(project_id):
        project_session = connection.create_session()
        return project_session
    else:
        raise ValueError(f'unable to find project {project_id}')
    

def _get_universe_session() -> Session:
    return UNIVERSE_DB_CONNECTION.create_session()


def _resolve_term(term_id: str,
                  term_type: str,
                  universe_session: Session,
                  project_session: Session) -> UTerm|PTerm|None:
    '''First find the term in the universe than in the current project'''
    uterms = universe._find_terms_in_data_descriptor(data_descriptor_id=term_type,
                                                     term_id=term_id,
                                                     session=universe_session,
                                                     settings=None)
    if uterms:
        return uterms[0]
    else:
        pterms = _find_terms_in_collection(collection_id=term_type,
                                           term_id=term_id,
                                           session=project_session,
                                           settings=None)
        result = pterms[0] if pterms else None
        return result


# TODO: support optionality of parts of composite.
# It is backtrack possible for more than one missing parts.
def _valid_value_for_term_composite(value: str,
                                    term: UTerm|PTerm,
                                    universe_session: Session,
                                    project_session: Session)\
                                        -> list[ValidationError]:
    result = list()
    separator = term.specs[api_settings.COMPOSITE_SEPARATOR_JSON_KEY]
    parts = term.specs[api_settings.COMPOSITE_PARTS_JSON_KEY]
    if separator:
        if separator in value:
            splits = value.split(separator)
            if len(splits) == len(parts):
                for index in range(0, len(splits)):
                    given_value = splits[index]
                    referenced_id = parts[index][api_settings.TERM_ID_JSON_KEY]
                    referenced_type = parts[index][api_settings.TERM_TYPE_JSON_KEY]
                    resolved_term = _resolve_term(referenced_id,
                                                  referenced_type,
                                                  universe_session,
                                                  project_session)
                    if resolved_term:
                        errors = _valid_value(given_value,
                                              resolved_term,
                                              universe_session,
                                              project_session)
                        result.extend(errors)
                    else:
                        msg = f'unable to find the term {referenced_id} ' + \
                              f'in {referenced_type}'
                        raise RuntimeError(msg)
            else:
                result.append(_create_term_error(value, term))
        else:
            result.append(_create_term_error(value, term))
    else:
        raise NotImplementedError(f'unsupported separator less term composite {term.id} ')
    return result


def _create_term_error(value: str, term: UTerm|PTerm) -> ValidationError:
    if isinstance(term, UTerm):
        return UniverseTermError(value, term)
    else:
        return ProjectTermError(value, term)


def _valid_value(value: str,
                 term: UTerm|PTerm,
                 universe_session: Session,
                 project_session: Session) -> list[ValidationError]:
    result = list()
    match term.kind:
        case TermKind.PLAIN:
            if term.specs[api_settings.DRS_SPECS_JSON_KEY] != value:
                result.append(_create_term_error(value, term))
        case TermKind.PATTERN:
            # OPTIM: Pattern can be compiled and stored for further matching.
            pattern_match = re.match(term.specs[api_settings.PATTERN_JSON_KEY], value)
            if pattern_match is None:
                result.append(_create_term_error(value, term))
        case TermKind.COMPOSITE:
            result.extend(_valid_value_for_term_composite(value, term,
                                                          universe_session,
                                                          project_session))
        case _:
            raise NotImplementedError(f'unsupported term kind {term.kind}')
    return result


def _check_and_strip_value(value: str) -> str:
    if not value:
        raise ValueError('value should be set')
    if result:= value.strip():
        return result
    else:
        raise ValueError('value should not be empty')


def _search_plain_term_and_valid_value(value: str,
                                       collection_id: str,
                                       project_session: Session) \
                                        -> str|None:
    where_expression = and_(Collection.id == collection_id,
                            PTerm.specs[api_settings.DRS_SPECS_JSON_KEY] == f'"{value}"')
    statement = select(PTerm).join(Collection).where(where_expression)
    term = project_session.exec(statement).one_or_none()
    return term.id if term else None


def _valid_value_against_all_terms_of_collection(value: str,
                                                 collection: Collection,
                                                 universe_session: Session,
                                                 project_session: Session) \
                                                     -> list[str]:
    if collection.terms:
        result = list()
        for pterm in collection.terms:
            _errors = _valid_value(value, pterm,
                                   universe_session,
                                   project_session)
            if not _errors:
                result.append(pterm.id)
        return result
    else:
        raise RuntimeError(f'collection {collection.id} has no term')


def _valid_value_against_given_term(value: str,
                                    collection_id: str,
                                    term_id: str,
                                    universe_session: Session,
                                    project_session: Session)\
                                        -> list[ValidationError]:
    try:
        terms = _find_terms_in_collection(collection_id,
                                          term_id,
                                          project_session,
                                          None)
        if terms:
            term = terms[0]
            result = _valid_value(value, term, universe_session, project_session)
        else:
            raise ValueError(f'unable to find term {term_id} ' +
                             f'in collection {collection_id}')
    except Exception as e:
        msg = f'unable to valid term {term_id} ' +\
              f'in collection {collection_id}'
        raise RuntimeError(msg) from e
    return result


def valid_term(value: str,
               project_id: str,
               collection_id: str,
               term_id: str) \
                  -> ValidationReport:
    """
    
    """
    value = _check_and_strip_value(value)
    with _get_universe_session() as universe_session, \
         _get_project_session_with_exception(project_id) as project_session:
        errors = _valid_value_against_given_term(value, collection_id, term_id,
                                                 universe_session, project_session)
        return ValidationReport(value, errors)


def _valid_term_in_collection(value: str,
                              project_id: str,
                              collection_id: str,
                              universe_session: Session,
                              project_session: Session) \
                                -> list[MatchingTerm]:
    value = _check_and_strip_value(value)
    result = list()
    collections = _find_collections_in_project(collection_id,
                                               project_session,
                                               None)
    if collections:
        collection = collections[0]
        match collection.term_kind:
            case TermKind.PLAIN:
                term_id_found = _search_plain_term_and_valid_value(value, collection_id,
                                                                   project_session)
                if term_id_found:
                    result.append(MatchingTerm(project_id, collection_id, term_id_found))
            case _:
                term_ids_found = _valid_value_against_all_terms_of_collection(value, collection,
                                                                              universe_session,
                                                                              project_session)
                for term_id_found in term_ids_found:
                    result.append(MatchingTerm(project_id, collection_id, term_id_found))
    else:
        msg = f'unable to find collection {collection_id}'
        raise ValueError(msg)
    return result


def valid_term_in_collection(value: str,
                             project_id: str,
                             collection_id: str) \
                               -> list[MatchingTerm]:
    """
    
    """
    with _get_universe_session() as universe_session, \
         _get_project_session_with_exception(project_id) as project_session:
        return _valid_term_in_collection(value, project_id, collection_id,
                                         universe_session, project_session)


def _valid_term_in_project(value: str,
                           project_id: str,
                           universe_session: Session,
                           project_session: Session) -> list[MatchingTerm]:
    result = list()
    collections = _get_all_collections_in_project(project_session)
    for collection in collections:
        result.extend(_valid_term_in_collection(value, project_id, collection.id,
                                                universe_session, project_session))
    return result


def valid_term_in_project(value: str, project_id: str) -> list[MatchingTerm]:
    """
    
    """
    with _get_universe_session() as universe_session, \
         _get_project_session_with_exception(project_id) as project_session:
        return _valid_term_in_project(value, project_id, universe_session, project_session)


def valid_term_in_all_projects(value: str) -> list[MatchingTerm]:
    """
    
    """
    result = list()
    with _get_universe_session() as universe_session:
        for project_id in get_all_projects():
            with _get_project_session_with_exception(project_id) as project_session:
                result.extend(_valid_term_in_project(value, project_id,
                                                     universe_session, project_session))
    return result


def _find_terms_in_collection(collection_id: str,
                              term_id: str,
                              session: Session,
                              settings: SearchSettings|None = None) -> Sequence[PTerm]:
    """Settings only apply on the term_id comparison."""
    where_expression = create_str_comparison_expression(field=PTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(PTerm).join(Collection).where(Collection.id==collection_id,
                                                     where_expression)
    results = session.exec(statement)
    result = results.all()    
    return result


def find_terms_in_collection(project_id:str,
                             collection_id: str,
                             term_id: str,
                             settings: SearchSettings|None = None) \
                                -> list[BaseModel]:
    """
    Finds one or more terms, based on the specified search settings, in the given collection of a project.
    This function performs an exact match on the `project_id` and `collection_id`, 
    and does **not** search for similar or related projects and collections.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    If any of the provided ids (`project_id`, `collection_id` or `term_id`) is not found,
    the function returns an empty list.
    
    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns zero or one Pydantic term instance in the list.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns zero, one or more
      Pydantic term instances in the list.

    :param project_id: A project id
    :type project_id: str
    :param collection_id: A collection
    :type collection_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A list of Pydantic term instances. Returns an empty list if no matches are found.
    :rtype: list[BaseModel]
    """
    result: list[BaseModel] = list()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            terms = _find_terms_in_collection(collection_id, term_id, session, settings)
            instantiate_pydantic_terms(terms, result)
    return result


def _find_terms_from_data_descriptor_in_project(data_descriptor_id: str,
                                                term_id: str,
                                                session: Session,
                                                settings: SearchSettings|None = None) \
                                                   -> Sequence[PTerm]:
    """Settings only apply on the term_id comparison."""
    where_expression = create_str_comparison_expression(field=PTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(PTerm).join(Collection).where(Collection.data_descriptor_id==data_descriptor_id,
                                                     where_expression)
    results = session.exec(statement)
    result = results.all()    
    return result


def find_terms_from_data_descriptor_in_project(project_id: str,
                                               data_descriptor_id: str,
                                               term_id: str,
                                               settings: SearchSettings|None = None) \
                                                  -> list[tuple[BaseModel, str]]:
    """
    Finds one or more terms in the given project which are instances of the given data descriptor
    in the universe, based on the specified search settings, in the given collection of a project.
    This function performs an exact match on the `project_id` and `data_descriptor_id`, 
    and does **not** search for similar or related projects and data descriptors.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    If any of the provided ids (`project_id`, `data_descriptor_id` or `term_id`) is not found,
    the function returns an empty list.
    
    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns zero or one Pydantic term instance and
      collection id in the list.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns zero, one or more
      Pydantic term instances and collection ids in the list.

    :param project_id: A project id
    :type project_id: str
    :param data_descriptor_id: A data descriptor
    :type data_descriptor_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A list of tuple of Pydantic term instances and related collection ids.
    Returns an empty list if no matches are found.
    :rtype: list[tuple[BaseModel, str]]
    """
    result = list()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            terms = _find_terms_from_data_descriptor_in_project(data_descriptor_id,
                                                                term_id,
                                                                session,
                                                                settings)
            for pterm in terms:
                collection_id = pterm.collection.id
                term = instantiate_pydantic_term(pterm)
                result.append((term, collection_id))
    return result


def find_terms_from_data_descriptor_in_all_projects(data_descriptor_id: str,
                                                    term_id: str,
                                                    settings: SearchSettings|None = None) \
                                                       -> list[tuple[BaseModel, str]]:
    """
    Finds one or more terms in all projects which are instances of the given data descriptor
    in the universe, based on the specified search settings, in the given collection of a project.
    This function performs an exact match on the `data_descriptor_id`, 
    and does **not** search for similar or related data descriptors.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    If any of the provided ids (`data_descriptor_id` or `term_id`) is not found,
    the function returns an empty list.
    
    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns zero or one Pydantic term instance and
      collection id in the list.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns zero, one or more
      Pydantic term instances and collection ids in the list.

    :param data_descriptor_id: A data descriptor
    :type data_descriptor_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A list of tuple of Pydantic term instances and related collection ids.
    Returns an empty list if no matches are found.
    :rtype: list[tuple[BaseModel, str]]
    """
    project_ids = get_all_projects()
    result = list()
    for project_id in project_ids:
        result.extend(find_terms_from_data_descriptor_in_project(project_id,
                                                                 data_descriptor_id,
                                                                 term_id,
                                                                 settings))
    return result


def _find_terms_in_project(term_id: str,
                           session: Session,
                           settings: SearchSettings|None) -> Sequence[PTerm]:
    where_expression = create_str_comparison_expression(field=PTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(PTerm).where(where_expression)
    results = session.exec(statement).all()
    return results


def find_terms_in_all_projects(term_id: str,
                               settings: SearchSettings|None = None) \
                                  -> list[BaseModel]:
    """
    Finds one or more terms, based on the specified search settings, in all projects.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    Terms are unique within a collection but may have some synonyms within a project.
    If the provided `term_id` is not found, the function returns an empty list.

    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A list of Pydantic term instances. Returns an empty list if no matches are found.
    :rtype: list[BaseModel]
    """
    project_ids = get_all_projects()
    result = list()
    for project_id in project_ids:
        result.extend(find_terms_in_project(project_id, term_id, settings))
    return result


def find_terms_in_project(project_id: str,
                          term_id: str,
                          settings: SearchSettings|None = None) \
                            -> list[BaseModel]:
    """
    Finds one or more terms, based on the specified search settings, in a project.
    This function performs an exact match on the `project_id` and 
    does **not** search for similar or related projects.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    Terms are unique within a collection but may have some synonyms within a project.
    If any of the provided ids (`project_id` or `term_id`) is not found, the function returns
    an empty list.

    :param project_id: A project id
    :type project_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A list of Pydantic term instances. Returns an empty list if no matches are found.
    :rtype: list[BaseModel]
    """
    result: list[BaseModel] = list()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            terms = _find_terms_in_project(term_id, session, settings)
            instantiate_pydantic_terms(terms, result)
    return result


def get_all_terms_in_collection(project_id: str,
                                collection_id: str)\
                                   -> list[BaseModel]:
    """
    Gets all terms of the given collection of a project.
    This function performs an exact match on the `project_id` and `collection_id`,
    and does **not** search for similar or related projects and collections.
    If any of the provided ids (`project_id` or `collection_id`) is not found, the function
    returns an empty list.

    :param project_id: A project id
    :type project_id: str
    :param collection_id: A collection id
    :type collection_id: str
    :returns: a list of Pydantic term instances.
    Returns an empty list if no matches are found.
    :rtype: list[BaseModel]
    """
    result = list()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _find_collections_in_project(collection_id,
                                                       session,
                                                       None)
            if collections:
                collection = collections[0]
                result = _get_all_terms_in_collection(collection)
    return result


def _find_collections_in_project(collection_id: str,
                                 session: Session,
                                 settings: SearchSettings|None) \
                                    -> Sequence[Collection]:
    where_exp = create_str_comparison_expression(field=Collection.id,
                                                 value=collection_id,
                                                 settings=settings)
    statement = select(Collection).where(where_exp)
    results = session.exec(statement)
    result = results.all()
    return result


def find_collections_in_project(project_id: str,
                                collection_id: str,
                                settings: SearchSettings|None = None) \
                                    -> list[dict]:
    """
    Finds one or more collections of the given project.
    This function performs an exact match on the `project_id` and 
    does **not** search for similar or related projects.
    The given `collection_id` is searched according to the search type specified in 
    the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `collection_id`.
    If any of the provided ids (`project_id` or `collection_id`) is not found, the function returns
    an empty list.
        
    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns zero or one collection context in the list.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns zero, one or more
      collection contexts in the list.

    :param project_id: A project id
    :type project_id: str
    :param collection_id: A collection id to be found
    :type collection_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A list of collection contexts.
    Returns an empty list if no matches are found.
    :rtype: list[dict]
    """
    result = list()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _find_collections_in_project(collection_id,
                                                       session,
                                                       settings)
            for collection in collections:
                result.append(collection.context)
    return result


def _get_all_collections_in_project(session: Session) -> list[Collection]:
    project = session.get(Project, api_settings.SQLITE_FIRST_PK)
    # Project can't be missing if session exists.
    return project.collections # type: ignore


def get_all_collections_in_project(project_id: str) -> list[str]:
    """
    Gets all collections of the given project.
    This function performs an exact match on the `project_id` and 
    does **not** search for similar or related projects.
    If the provided `project_id` is not found, the function returns an empty list.

    :param project_id: A project id
    :type project_id: str
    :returns: A list of collection ids.
    Returns an empty list if no matches are found.
    :rtype: list[str]
    """
    result = list()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _get_all_collections_in_project(session)
            for collection in collections:
                result.append(collection.id)
    return result


def _get_all_terms_in_collection(collection: Collection) -> list[BaseModel]:
    result: list[BaseModel] = list()
    instantiate_pydantic_terms(collection.terms, result)
    return result


def get_all_terms_in_project(project_id: str) -> list[BaseModel]:
    """
    Gets all terms of the given project.
    This function performs an exact match on the `project_id` and 
    does **not** search for similar or related projects.
    Terms are unique within a collection but may have some synonyms in a project.
    If the provided `project_id` is not found, the function returns an empty list.

    :param project_id: A project id
    :type project_id: str
    :returns: A list of Pydantic term instances.
    Returns an empty list if no matches are found.
    :rtype: list[BaseModel]
    """
    result = list()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _get_all_collections_in_project(session)
            for collection in collections:
                # Term may have some synonyms in a project.
                result.extend(_get_all_terms_in_collection(collection))
    return result


def get_all_terms_in_all_projects() -> list[BaseModel]:
    """
    Gets all terms of all projects.

    :returns: A list of Pydantic term instances.
    :rtype: list[BaseModel]
    """
    project_ids = get_all_projects()
    result = list()
    for project_id in project_ids:
        result.extend(get_all_terms_in_project(project_id))
    return result


def find_project(project_id: str) -> dict|None:
    """
    Finds a project.
    This function performs an exact match on the `project_id` and 
    does **not** search for similar or related projects.
    If the provided `project_id` is not found, the function returns `None`.
    
    :param project_id: A project id to be found
    :type project_id: str
    :returns: The specs of the project found.
    Returns `None` if no matches are found.
    :rtype: dict|None
    """
    result = None
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            project = session.get(Project, api_settings.SQLITE_FIRST_PK)
            # Project can't be missing if session exists.
            result = project.specs # type: ignore
    return result


def get_all_projects() -> list[str]:
    """
    Gets all projects.
    
    :returns: A list of project ids.
    :rtype: list[str]
    """
    return ['cmip6plus'] # DEBUG TODO: to be implemented


if __name__ == "__main__":
    vr = valid_term('0241206-0241207', 'cmip6plus', 'time_range', 'daily')
    if vr:
        print('OK')
    else:
        print(vr)
        from cmipld.api import BasicValidationErrorVisitor
        visitor = BasicValidationErrorVisitor()
        for error in vr.errors:
            print(error.accept(visitor))