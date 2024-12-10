from pydantic import BaseModel
from cmipld import get_pydantic_class
from sqlmodel import Session, select
from cmipld.api import SearchSettings, create_str_comparison_expression, SearchType
import cmipld.settings as api_settings
import cmipld.db as db
from cmipld.db.models.project import Project, Collection, PTerm
from cmipld.db.models.mixins import TermKind
import re
from cmipld.api.models import GenericTermComposite
import cmipld.api.univers as univers
from cmipld.db.models.univers import UTerm

############## DEBUG ##############
# TODO: to be deleted.
# The following instructions are only temporary as long as a complet data managment will be implmented.
UNIVERS_DB_CONNECTION = db.DBConnection(db.UNIVERS_DB_FILE_PATH, 'univers', False)
###################################


def _get_project_connection(project_id: str) -> db.DBConnection|None:
    ############## DEBUG ##############
    # TODO: to be deleted.
    # The following instructions are only temporary as long as a complet data managment will be implmented.
    return db.DBConnection(db.CMIP6PLUS_DB_FILE_PATH, 'cmip6plus', False)
    ###################################


def _resolve_term(term_id: str, term_type: str, project_session: Session) -> UTerm|PTerm:
    '''First find the term in the univers than in the current project'''
    result = None
    with UNIVERS_DB_CONNECTION.create_session() as univers_session:
        uterm: UTerm = univers._find_terms_in_data_descriptor(data_descriptor_id=term_type,
                                                              term_id=term_id,
                                                              session=univers_session,
                                                              settings=None)
        if uterm:
            result = uterm
        else:
            pterm:PTerm = _find_terms_in_collection(collection_id=term_type,
                                                    term_id=term_id,
                                                    session=project_session,
                                                    settings=None)
            result = pterm
    return result


# TODO: support optionality of parts of composite.
# It is backtrack possible for more than one missing parts.
def _valid_term_composite(value: str,
                          term: UTerm|PTerm,
                          project_session: Session) -> bool:
    composite = GenericTermComposite(**term.specs)
    if composite.separator:
        if composite.separator in value:
            splits = value.split(composite.separator)
            if len(splits) == len(composite.parts):
                result = True
                for index in range(0, len(splits)):
                    given_value = splits[index]
                    referenced_id = composite.parts[index].id
                    referenced_type = composite.parts[index].type
                    resolved_term = _resolve_term(referenced_id,
                                                  referenced_type,
                                                  project_session)
                    if resolved_term:
                        is_valid = _valid_term(given_value,
                                               resolved_term,
                                               project_session)
                        if is_valid:
                            continue
                        else:
                            result = False
                            break
                    else:
                        msg = f'unable to find the term {referenced_id} ' + \
                              f'in {referenced_type}'
                        raise RuntimeError(msg)
            else:
                result = False
        else:
            result = False
    else:
        raise NotImplementedError(f'unsupported separatorless term composite {term.id} ' +
                                  f'in collection {term.collection.id}')
    return result


# Return why (as Exception?)
def _valid_term(value: str, term: UTerm|PTerm, project_session: Session) -> bool:
    match term.kind:
        case TermKind.PLAIN:
            result = term.specs[api_settings.DRS_SPECS_JSON_KEY] == value
        case TermKind.PATTERN:
            # OPTIM: Pattern can be compiled and stored for further matching.
            pattern_match = re.match(term.specs[api_settings.PATTERN_JSON_KEY], value)
            result = pattern_match is not None
        case TermKind.COMPOSITE:
            _valid_term_composite(value, term, project_session)
        case _:
            raise NotImplementedError(f'unsupported term kind {term.kind}')
    return result


def _valid_plain_term(value: str,
                      collection_id: str,
                      term_id: str,
                      session: Session) -> bool:
    try:
        term: PTerm = _find_terms_in_collection(collection_id,
                                                term_id,
                                                session,
                                                None)
    except Exception:
        raise ValueError(f'unable to find term {term_id} ' +
                         f'in collection {collection_id}')
    try:
        result = _valid_term(value, term, session)
    except Exception as e:
        msg = f'unable to valid term {term_id} ' +\
              f'in collection {collection_id}'
        raise RuntimeError(msg) from e
    return result


def valid_term_in_collection(value: str,
                             project_id: str,
                             collection_id: str,
                             term_id: str|None = None) \
                               -> bool:
    """
    TODO
    raise ValueError
    """
    if not value:
        raise ValueError('value should be set')
    if value:= value.strip():
        if connection:=_get_project_connection(project_id):
            with connection.create_session() as session:
                if term_id:
                    result = _valid_plain_term(value, collection_id,
                                               term_id, session)
                else:
                    collection = _find_collections_in_project(collection_id,
                                                              session,
                                                              None)
                    # TODO: untested
                    match collection.term_kind:
                        case TermKind.PLAIN:
                            result = _valid_plain_term(value, collection_id,
                                                       value, session)
                        case TermKind.PATTERN | TermKind.COMPOSITE:
                            if collection:
                                for term in collection.terms:
                                    is_valided = _valid_term(value, term, session)
                                    if is_valided:
                                        break
                                result = is_valided
                            else:
                                msg = f'unable to find collection {collection_id}'
                                raise ValueError(msg)
                return result
        else:
            raise ValueError(f'unable to find project {project_id}')
    else:
        raise ValueError('value should not be empty')


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
                             settings: SearchSettings|None = None) \
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
                          settings: SearchSettings|None = None) \
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
            collection = _find_collections_in_project(collection_id,
                                                      session,
                                                      None)
            if collection:
                result = dict()
                terms = _get_all_terms_in_collection(collection)
                for term in terms:
                    result[term.id] = term
    return result


def _find_collections_in_project(collection_id: str,
                                 session: Session,
                                 settings: SearchSettings|None) \
                                    -> Collection|list[Collection]|None:
    where_exp = create_str_comparison_expression(field=Collection.id,
                                                 value=collection_id,
                                                 settings=settings)
    statement = select(Collection).where(where_exp)
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
            collections = _find_collections_in_project(collection_id,
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


def _get_all_collections_in_project(session: Session) -> list[Collection]|None:
    project = session.get(Project, api_settings.SQLITE_FIRST_PK)
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
            collections = _get_all_collections_in_project(session)
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
            collections = _get_all_collections_in_project(session)
            if collections:
                result = dict()
                for collection in collections:
                    # Term may have some sysnonyms within a project.
                    result[collection.id] = dict()
                    terms = _get_all_terms_in_collection(collection)
                    for term in terms:
                        result[collection.id][term.id] = term
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
            project = session.get(Project, api_settings.SQLITE_FIRST_PK)
            result = project.specs if project else None
    return result


def get_all_projects() -> dict[str: dict]:
    """
    Gets all the projects.
    
    :returns: A dictionary that maps project ids to their specs.
    :rtype: dict[str: dict]
    """
    return ['cmip6plus'] # TODO: to be implemented


if __name__ == "__main__":
    #valid_term_in_collection('20241206-20241207', 'cmip6plus', 'time_range')
    #valid_term_in_collection('IPSL', 'cmip6plus', 'institution_id')
    print(valid_term_in_collection('IPSL', 'cmip6plus', 'institution_id', 'ipsl'))