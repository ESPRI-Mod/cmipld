from typing import Generator

import pytest

import cmipld.api.univers as univers
from cmipld.api import SearchSettings, SearchType

_SOME_DATA_DESCRIPTOR_IDS = ('institution', 'product', 'variable')
_SOME_TERM_IDS = ('ipsl', 'observations', 'airmass')
_SETTINGS = SearchSettings(type=SearchType.LIKE)


def _provide_data_descriptor_ids() -> Generator[str]:
    for id in _SOME_DATA_DESCRIPTOR_IDS:
        yield id


@pytest.fixture(params=_provide_data_descriptor_ids())
def data_descriptor_id(request) -> str:
    return request.param


def _provide_term_ids() -> Generator[str]:
    for id in _SOME_TERM_IDS:
        yield id


@pytest.fixture(params=_provide_term_ids())
def term_id(request) -> str:
    return request.param


def test_get_all_terms_in_univers() -> None:
    univers.get_all_terms_in_univers()


def test_get_all_data_descriptors_in_univers() -> None:
    univers.get_all_data_descriptors_in_univers()


def test_get_terms_in_data_descriptor(data_descriptor_id) -> None:
    univers.get_all_terms_in_data_descriptor(data_descriptor_id)
        

def test_find_term_in_data_descriptor(data_descriptor_id, term_id) -> None:
    univers.find_terms_in_data_descriptor(data_descriptor_id, term_id)
    univers.find_terms_in_data_descriptor(data_descriptor_id, term_id, _SETTINGS)


def test_find_terms_in_univers(term_id) -> None:
    univers.find_terms_in_univers(term_id)
    univers.find_terms_in_univers(term_id, settings=_SETTINGS)


def test_find_data_descriptor_in_univers(data_descriptor_id) -> None:
    univers.find_data_descriptors_in_univers(data_descriptor_id)
    univers.find_data_descriptors_in_univers(data_descriptor_id, settings=_SETTINGS)    