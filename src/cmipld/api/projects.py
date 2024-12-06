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


def _find_terms_in_project(term_id: str,
                           settings: SearchSettings,
                           session: Session) -> list[PTerm]:
    where_expression = create_str_comparison_expression(field=PTerm.id,
                                                        value=term_id,
                                                        settings=settings)
    statement = select(PTerm).where(where_expression)
    results = session.exec(statement).all()
    return results


def find_terms_in_project(project_id: str,
                          term_id: str,
                          settings: SearchSettings = SearchSettings()) \
                            -> dict[str, dict[str, type[BaseModel]]]:
    """
    Finds one or more terms of the univers.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    The given `term_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE`, `STARTS_WITH` and `ENDS_WITH` may return multiple results).
    As terms are unique within a collection but may have some synonyms within a project,
    the result maps every term found to their collection.
    If the provided `term_id` or `project_id` is not found, the function returns an empty dictionary.

    Behavior based on search type:
    - `EXACT` or `REGEX`: returns 0 or 1 result per data descriptor.
    - `LIKE`, `STARTS_WITH` and `ENDS_WITH`: may return multiple results per data descriptor.

    :param project_id: A project id to be found
    :type project_id: str
    :param term_id: A term id to be found
    :type term_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dictionary that maps collection ids to a mapping of term ids and their corresponding Pydantic model instances.
    Returns an empty dictionary if no matches are found.
    :rtype: dict[str, dict[str, type[BaseModel]]]
    """
    result = dict()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            terms = _find_terms_in_project(term_id, settings, session)
            for term in terms:
                if term.collection.id not in result:
                    result[term.collection.id] = dict()
                term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
                result[term.collection.id][term.id] = term_class(**term.specs)
    return result


def get_all_terms_in_collection(project_id: str,
                                collection_id: str)\
                                   -> dict[str, type[BaseModel]]:
    """
    Gets all the terms of the given collection.
    This function performs an exact match on the `project_id` and `collection_id`, and does **not** search for similar or related projects and collections.
    If the provided `project_id` or `collection_id` is not found, the function returns an empty dictionary.

    :param project_id: A project id to be found
    :type project_id: str
    :param collection_id: A collection id to be found
    :type collection_id: str
    :returns: a dictionary that maps term ids to their corresponding Pydantic instances.
    Returns an empty dictionary if no matches are found.
    :rtype: dict[str, type[BaseModel]]
    """
    result = dict()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _find_collections_in_project(project_id,
                                                       collection_id,
                                                       SearchSettings(),
                                                       session)
            if collections:
                collection = collections[0]
                terms = _get_all_terms_in_collection(collection)
                for term in terms:
                    result[term.id] = term
    return result


def _find_collections_in_project(project_id: str,
                                 collection_id,
                                 settings, session) -> list[Collection]:
    where_exp = create_str_comparison_expression(field=Collection.id,
                                                 value=collection_id,
                                                 settings=settings)
    statement = select(Collection).join(Project).where(Project.id == project_id, where_exp)
    results = session.exec(statement).all()
    return results


def find_collections_in_project(project_id: str,
                                collection_id: str,
                                settings: SearchSettings = SearchSettings()) \
                                    -> dict[str, dict]:
    """
    Finds one or more collections of the given project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    The given `collection_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE`, `STARTS_WITH` and `ENDS_WITH` may return multiple results).
    As a result, the function returns a dictionary that maps collection ids to their context.
    If the provided `collection_id` or `project_id` is not found, the function returns an empty dictionary.
    
    Behavior based on search type:
    - `EXACT` or `REGEX`: returns 0 or 1 result.
    - `LIKE`, `STARTS_WITH` and `ENDS_WITH`: may return multiple results.

    :param project_id: A project id to be found
    :type project_id: str
    :param collection_id: A collection id to be found
    :type collection_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dictionary that maps collection ids to their context.
    Returns an empty dictionary if no matches are found.
    :rtype: dict[str, dict]
    """
    result = dict()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _find_collections_in_project(project_id,
                                                       collection_id,
                                                       settings,
                                                       session)
            for collection in collections:
                result[collection.id] = collection.context
    return result


def _get_all_collections_in_project(project_id: str, session: Session) -> list[Collection]:
    statement = select(Project).where(Project.id == project_id)
    project = session.exec(statement).one_or_none()
    return project.collections if project else list()


def _get_all_terms_in_collection(collection: Collection) -> list[type[BaseModel]]:
    result = list()
    for term in collection.terms:
        term_class = get_pydantic_class(term.specs[api_settings.TERM_TYPE_JSON_KEY])
        result.append(term_class(**term.specs))
    return result


def get_all_collections_in_project(project_id) -> dict[str, dict]:
    """
    Gets all the collections of the given project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.

    :param project_id: A project id to be found
    :type project_id: str
    :returns: A dictionary that maps collection ids to their context.
    Returns an empty dictionary if no matches are found.
    :rtype: dict[str, dict]
    """
    result = dict()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _get_all_collections_in_project(project_id, session)
            for collection in collections:
                result[collection.id] = collection.context
    return result


def get_all_terms_in_project(project_id: str) -> dict[str, dict[str, type[BaseModel]]]:
    """
    Gets all the terms of the given project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    As terms are unique within a collection but may have some synonyms within a project,
    this function returns a dictionary that maps every term to their collection.
    If the provided `project_id` is not found, the function returns an empty dictionary.

    :param project_id: A project id to be found
    :type project_id: str
    :returns: A dictionary that maps collection ids to a mapping of term ids and their corresponding Pydantic model instances.
    Returns an empty dictionary if no matches are found.
    :rtype: dict[str, dict[str, type[BaseModel]]]
    """
    result = dict()
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            collections = _get_all_collections_in_project(project_id, session)
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


def find_project(project_id: str) -> dict:
    """
    Finds one project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    
    :param project_id: A project id to be found
    :type project_id: str
    :returns: The specs of the project.
    Returns an empty dictionary if no matches are found.
    :rtype: dict
    """
    if connection:=_get_project_connection(project_id):
        with connection.create_session() as session:
            project = _find_project(project_id, session)
            result = project.specs
    else:
        result = dict()
    return result


def get_all_projects() -> dict[str: dict]:
    return ['cmip6plus'] # TODO: to be implemented


if __name__ == "__main__":
    from cmipld.api import SearchType
    search_settings = SearchSettings(case_sensitive=False, type=SearchType.LIKE)
    print(find_terms_in_project('cmip6plus', 'iPsl', search_settings))