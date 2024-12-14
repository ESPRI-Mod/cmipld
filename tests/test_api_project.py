import pytest

from typing import Generator

import cmipld.api.projects as projects
from cmipld.api import SearchSettings, SearchType

_SOME_PROJECT_IDS = ['cmip6plus']
_SOME_COLLECTION_IDS = ['institution_id', 'time_range', 'source_id']
_SOME_DATA_DESCRIPTOR_IDS = ['organisation', 'time_range', 'source']
_SOME_TERM_IDS = ['ipsl', 'daily', 'miroc6']
_SOME_VALIDATION_REQUESTS = [
    (0, ('IPSL', 'cmip6plus', 'institution_id', 'ipsl')),
    (1, ('IPL', 'cmip6plus', 'institution_id', 'ipsl')),
    (0, ('IPSL', 'cmip6plus', 'institution_id')),
    (1, ('IPL', 'cmip6plus', 'institution_id')),
    (0, ('20241206-20241207', 'cmip6plus', 'time_range', 'daily')),
    (2, ('0241206-0241207', 'cmip6plus', 'time_range', 'daily')),
    (0, ('20241206-20241207', 'cmip6plus', 'time_range')),
    (1, ('0241206-0241207', 'cmip6plus', 'time_range'))]
_SETTINGS = SearchSettings(type=SearchType.LIKE)


def _provide_validation_request() -> Generator:
    for validation_request in _SOME_VALIDATION_REQUESTS:
        yield validation_request


@pytest.fixture(params=_provide_validation_request())
def validation_request(request) -> tuple:
    return request.param


def _provide_project_ids() -> Generator:
    for project_id in _SOME_PROJECT_IDS:
        yield project_id


@pytest.fixture(params=_provide_project_ids())
def project_id(request) -> str:
    return request.param


def _provide_collection_ids() -> Generator:
    for collection_id in _SOME_COLLECTION_IDS:
        yield collection_id


@pytest.fixture(params=_provide_collection_ids())
def collection_id(request) -> str:
    return request.param


def _provide_data_descriptor_ids() -> Generator:
    for collection_id in _SOME_DATA_DESCRIPTOR_IDS:
        yield collection_id


@pytest.fixture(params=_provide_data_descriptor_ids())
def data_descriptor_id(request) -> str:
    return request.param


def _provide_term_ids() -> Generator:
    for term_id in _SOME_TERM_IDS:
        yield term_id


@pytest.fixture(params=_provide_term_ids())
def term_id(request) -> str:
    return request.param


def test_get_all_projects() -> None:
    projects.get_all_projects()


def test_get_all_terms_in_all_projects() -> None:
    projects.get_all_terms_in_all_projects()


def test_find_project(project_id) -> None:
    projects.find_project(project_id)


def test_get_all_terms_in_project(project_id) -> None:
    projects.get_all_terms_in_project(project_id)


def test_get_all_collections_in_project(project_id) -> None:
    projects.get_all_collections_in_project(project_id)


def test_find_collections_in_project(project_id, collection_id) -> None:
    projects.find_collections_in_project(project_id, collection_id)
    projects.find_collections_in_project(project_id, collection_id, _SETTINGS)


def test_get_all_terms_in_collection(project_id, collection_id) -> None:
    projects.get_all_terms_in_collection(project_id, collection_id)


def test_find_terms_in_project(project_id, term_id) -> None:
    projects.find_terms_in_project(project_id, term_id)
    projects.find_terms_in_project(project_id, term_id, _SETTINGS)


def test_find_terms_in_all_projects(term_id) -> None:
    projects.find_terms_in_all_projects(term_id)
    projects.find_terms_in_all_projects(term_id, _SETTINGS)


def test_find_terms_in_collection(project_id, collection_id, term_id) -> None:
    projects.find_terms_in_collection(project_id, collection_id, term_id)
    projects.find_terms_in_collection(project_id, collection_id, term_id, _SETTINGS)


def test_find_terms_from_data_descriptor_in_project(project_id, data_descriptor_id, term_id) -> None:
    projects.find_terms_from_data_descriptor_in_project(project_id, data_descriptor_id, term_id)
    projects.find_terms_from_data_descriptor_in_project(project_id,
                                                        data_descriptor_id,
                                                        term_id,
                                                        _SETTINGS)


def test_find_terms_from_data_descriptor_in_all_projects(data_descriptor_id,
                                                         term_id) -> None:
    projects.find_terms_from_data_descriptor_in_all_projects(data_descriptor_id, term_id)
    projects.find_terms_from_data_descriptor_in_all_projects(data_descriptor_id,
                                                             term_id,
                                                             _SETTINGS)


def test_valid_term_in_collection(validation_request) -> None:
    nb_errors, parameters = validation_request
    vr = projects.valid_term_in_collection(*parameters)
    assert nb_errors == len(vr), f'unmatching number of errors for parameters {parameters}'
