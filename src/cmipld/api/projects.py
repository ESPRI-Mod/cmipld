from sqlmodel import Session, select
from cmipld.api import SearchSettings, create_str_comparison_expression

import cmipld.db as db
from cmipld.db.models.project import Project


############## DEBUG ##############
# TODO: to be deleted.
# The following instructions are only temporary as long as a complet data managment will be implmented.
CMIP6PLUS_DB_CONNECTION = db.DBConnection(db.CMIP6PLUS_DB_FILE_PATH, 'cmip6plus', False)
###################################


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
    find_project('cmip6plus')
