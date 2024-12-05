from pydantic import BaseModel
from cmipld import get_pydantic_class
from sqlmodel import Session, select
from cmipld.api import SearchSettings, create_str_comparison_expression

import cmipld.settings as settings
import cmipld.db as db
from cmipld.db.models.project import Project, Collection


############## DEBUG ##############
# TODO: to be deleted.
# The following instructions are only temporary as long as a complet data managment will be implmented.
CMIP6PLUS_DB_CONNECTION = db.DBConnection(db.CMIP6PLUS_DB_FILE_PATH, 'cmip6plus', False)
###################################


def _get_all_collections_in_project(project_id: str, session: Session) -> list[Collection]:
    statement = select(Project).where(Project.id == project_id)
    project = session.exec(statement).one()
    return project.collections


def _get_all_terms_in_collection(collection: Collection) -> list[type[BaseModel]]:
    result = list()
    for term in collection.terms:
        term_class = get_pydantic_class(term.specs[settings.TERM_TYPE_JSON_KEY])
        result.append(term_class(**term.specs))
    return result


def get_all_terms_in_project(project_id: str) -> dict[str, dict[str, type[BaseModel]]]:
    """
    Gets all the terms of the given project.
    This function performs an exact match on the `project_id` and does **not** search for similar or related projects.
    As terms are unique within a collection but may have some synonyms within a project,
    the result maps every term to their collection.

    :returns: A dictionary that maps collection ids to a mapping of term ids and their corresponding Pydantic model instances.
    :rtype: dict[str, dict[str, type[BaseModel]]]
    """
    with CMIP6PLUS_DB_CONNECTION.create_session() as session:
        collections = _get_all_collections_in_project(project_id, session)
        result = dict()
        for collection in collections:
            # Term may have some sysnonyms within a project.
            result[collection.id] = dict()
            terms = _get_all_terms_in_collection(collection)
            for term in terms:
                result[collection.id][term.id] = term
    return result


def _find_project(project_id: str,
                  settings: SearchSettings,
                  session: Session) -> list[Project]:
    where_expression = create_str_comparison_expression(field=Project.id,
                                                        value=project_id,
                                                        settings=settings)
    statement = select(Project).where(where_expression)
    results = session.exec(statement).all()
    return results


def find_project(project_id: str,
                 settings: SearchSettings = SearchSettings()) -> dict[str: dict]:
    """
    Finds one or more projects.
    The given `project_id` is searched according to the search type specified in the parameter `settings`,
    which allows a flexible matching (e.g., `LIKE`, `STARTS_WITH` and `ENDS_WITH` may return multiple results).
    As a result, the function returns a dictionary that maps project ids to their context.
    If the provided `project_id` is not found, the function returns an empty dictionary.
    
    Behavior based on search type:
    - `EXACT` or `REGEX`: returns 0 or 1 result.
    - `LIKE`, `STARTS_WITH` and `ENDS_WITH`: may return multiple results.

    :param project_id: A project id to be found
    :type project_id: str
    :param settings: The search settings
    :type settings: SearchSettings
    :returns: A dictionary that maps project ids to their context.
    Returns an empty dictionary if no matches are found.
    :rtype: dict[str, dict]
    """
    with CMIP6PLUS_DB_CONNECTION.create_session() as session:
        result = dict()
        projects = _find_project(project_id, settings, session)
        for project in projects:
            result[project.id] = project.specs
    return result


if __name__ == "__main__":
    get_all_terms_in_project('cmip6plus')