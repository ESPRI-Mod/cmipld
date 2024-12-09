from pydantic import BaseModel
from cmipld import get_pydantic_class
from sqlmodel import Session, select
from cmipld.api import SearchSettings, create_str_comparison_expression

import cmipld.settings as api_settings
import cmipld.db as db
from cmipld.db.models.project import Project, Collection, PTerm


def _get_project_connection(project_id: str) -> db.DBConnection|None:
    ############## DEBUG ##############
    # TODO: to be deleted.
    # The following instructions are only temporary as long as a complet data managment will be implmented.
    return db.DBConnection(db.CMIP6PLUS_DB_FILE_PATH, 'cmip6plus', False)
    ###################################


def _find_terms_in_collection(collection_id: str,
                              term_id: str,
                              session: Session,
                              settings: SearchSettings|None = None) -> PTerm|list[PTerm]|None:
    """Settings only apply on the term_id comparison."""
    where_expression = create_str_comparison_expression(field=PTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(PTerm).join(Collection).where(Collection.id==collection_id,
                                                     where_expression)
    results = session.exec(statement)
    if settings is None or SearchType.EXACT == settings.type:
        # As we compare id, it can't be more than one result.
        result = results.one_or_none()
    else:
        result = results.all()
    return result


def find_terms_in_collection(project_id:str,
                             collection_id: str,
                             term_id: str,
                             settings: SearchSettings|None) \
                                -> BaseModel|dict[str: BaseModel]|None:
    """
    Finds one or more terms, based on the specified search settings, in the given collection of a project.
    This function performs an exact match on the `project_id` and `collection_id`, and does **not** search for similar or related projects and collections.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    If any of the provided ids (`project_id`, `collection_id` or `term_id`) is not found, the function returns `None`.
    
    Behavior based on search type:
    - `EXACT`: and absence of `settings`: returns `None` or a Pydantic model term instance.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns `None` or a dictionary that maps term ids found
    to their corresponding Pydantic model instances.

    :param project_id: A project id
    :type project_id: str
    :param collection_id: A collection
    :type collection_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A Pydantic model term instance or a dictionary that maps term ids found to their corresponding Pydantic model instances.
    Returns `None` if no matches are found.
    :rtype: BaseModel|dict[str: BaseModel]|None
    """
    result = None
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            terms = _find_terms_in_collection(collection_id, term_id, session, settings)
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


def _find_terms_in_project(term_id: str,
                           session: Session,
                           settings: SearchSettings|None) -> list[PTerm]:
    where_expression = create_str_comparison_expression(field=PTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(PTerm).where(where_expression)
    results = session.exec(statement).all()
    return results


def find_terms_in_project(project_id: str,
                          term_id: str,
                          settings: SearchSettings|None) \
                            -> dict[str, BaseModel]|\
                               dict[str, dict[str, BaseModel]]|\
                               None:
    """
    Finds one or more terms, based on the specified search settings, in a project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `term_id`.
    As terms are unique within a collection but may have some synonyms within a project,
    the result maps every term found to their collection.
    If any of the provided ids (`project_id` or `term_id`) is not found, the function returns `None`.

    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns `None` or a dictionary that maps
      collection ids to a Pydantic model term instance.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns `None` or a dictionary that maps
      collection ids to a mapping of term ids and their corresponding Pydantic model instances.

    :param project_id: A project id
    :type project_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A dictionary that maps collection ids to a Pydantic model term instance
    or a dictionary that maps collection ids
    to a mapping of term ids and their corresponding Pydantic model instances.
    Returns `None` if no matches are found.
    :rtype: dict[str, BaseModel]|dict[str, dict[str, BaseModel]]|None
    """
    result = None
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            terms = _find_terms_in_project(term_id, session, settings)
            if terms:
                result = dict()
                for term in terms:
                    term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
                    if settings is None or SearchType.EXACT == settings.type:
                        result[term.collection.id] = term_class(**term.specs)
                    else:
                        if term.collection.id not in result:
                            result[term.collection.id] = dict()
                        result[term.collection.id][term.id] = term_class(**term.specs)
    return result


def get_all_terms_in_collection(project_id: str,
                                collection_id: str)\
                                   -> dict[str, BaseModel]|None:
    """
    Gets all the terms of the given collection of a project.
    This function performs an exact match on the `project_id` and `collection_id`, and does **not** search for similar or related projects and collections.
    If any of the provided ids (`project_id` or `collection_id`) is not found, the function returns `None`.

    :param project_id: A project id
    :type project_id: str
    :param collection_id: A collection id
    :type collection_id: str
    :returns: a dictionary that maps term ids to their corresponding Pydantic instances.
    Returns `None` if no matches are found.
    :rtype: dict[str, BaseModel]|None
    """
    result = None
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collection = _find_collections_in_project(project_id,
                                                      collection_id,
                                                      session,
                                                      None)
            if collection:
                result = dict()
                terms = _get_all_terms_in_collection(collection)
                for term in terms:
                    result[term.id] = term
    return result


def _find_collections_in_project(project_id: str,
                                 collection_id: str,
                                 session: Session,
                                 settings: SearchSettings|None) -> Collection|list[Collection]|None:
    where_exp = create_str_comparison_expression(field=Collection.id,
                                                 value=collection_id,
                                                 settings=settings)
    statement = select(Collection).join(Project).where(Project.id == project_id, where_exp)
    results = session.exec(statement)
    if settings is None or SearchType.EXACT == settings.type:
        # As we compare id, it can't be more than one result.
        result = results.one_or_none()
    else:
        result = results.all()
    return result


def find_collections_in_project(project_id: str,
                                collection_id: str,
                                settings: SearchSettings|None = None) \
                                    -> dict|dict[str, dict]|None:
    """
    Finds one or more collections of the given project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    The given `collection_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE` may return multiple results).
    If the parameter `settings` is `None`, this function performs an exact match on the `collection_id`.
    If any of the provided ids (`project_id` or `collection_id`) is not found, the function returns `None`.
        
    Behavior based on search type:
    - `EXACT` and absence of `settings`: returns `None` or a collection context.
    - `REGEX`, `LIKE`, `STARTS_WITH` and `ENDS_WITH`: returns `None` or 
      dictionary that maps collection ids to their context.

    :param project_id: A project id
    :type project_id: str
    :param collection_id: A collection id to be found
    :type collection_id: str
    :param settings: The search settings
    :type settings: SearchSettings|None
    :returns: A collection context or dictionary that maps collection ids to their context.
    Returns `None` if no matches are found.
    :rtype: dict|dict[str, dict]|None
    """
    result = None
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _find_collections_in_project(project_id,
                                                       collection_id,
                                                       session,
                                                       settings)
            if collections:
                if settings is None or SearchType.EXACT == settings.type:
                    result = collections.context
                else:
                    result = dict()
                    for collection in collections:
                        result[collection.id] = collection.context
    return result


def _get_all_collections_in_project(project_id: str, session: Session) -> list[Collection]|None:
    statement = select(Project).where(Project.id == project_id)
    project = session.exec(statement).one_or_none()
    return project.collections if project else None


def get_all_collections_in_project(project_id: str) -> dict[str, dict]|None:
    """
    Gets all the collections of the given project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    If the provided `project_id` is not found, the function returns `None`.

    :param project_id: A project id
    :type project_id: str
    :returns: A dictionary that maps collection ids to their context.
    Returns `None` if no matches are found.
    :rtype: dict[str, dict]|None
    """
    result = None
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _get_all_collections_in_project(project_id, session)
            if collections:
                result = dict()
                for collection in collections:
                    result[collection.id] = collection.context
    return result


def _get_all_terms_in_collection(collection: Collection) -> list[BaseModel]:
    result = list()
    for term in collection.terms:
        term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
        result.append(term_class(**term.specs))
    return result


def get_all_terms_in_project(project_id: str) -> dict[str, dict[str, BaseModel]]|None:
    """
    Gets all the terms of the given project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    As terms are unique within a collection but may have some synonyms within a project,
    this function returns a dictionary that maps every term to their collection.
    If the provided `project_id` is not found, the function returns `None`.

    :param project_id: A project id
    :type project_id: str
    :returns: A dictionary that maps collection ids to a mapping of term ids and their corresponding Pydantic model instances.
    Returns `None` if no matches are found.
    :rtype: dict[str, dict[str, BaseModel]]|None
    """
    result = None
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _get_all_collections_in_project(project_id, session)
            if collections:
                result = dict()
                for collection in collections:
                    # Term may have some sysnonyms within a project.
                    result[collection.id] = dict()
                    terms = _get_all_terms_in_collection(collection)
                    for term in terms:
                        result[collection.id][term.id] = term
    return result


def _find_project(project_id: str, session: Session) -> Project|None:
    statement = select(Project).where(Project.id == project_id)
    result = session.exec(statement).one_or_none()
    return result


def find_project(project_id: str) -> dict|None:
    """
    Finds a project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
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
            project = _find_project(project_id, session)
            if project:
                result = project.specs
    return result


def get_all_projects() -> dict[str: dict]:
    """
    Gets all the projects.
    
    :returns: A dictionary that maps project ids to their specs.
    :rtype: dict[str: dict]
    """
    return ['cmip6plus'] # TODO: to be implemented


if __name__ == "__main__":
    from cmipld.api import SearchType
    search_settings = SearchSettings(case_sensitive=False, type=SearchType.LIKE)
    print(find_terms_in_collection('cmip6plus', 'institution_id', 'Psl', search_settings))