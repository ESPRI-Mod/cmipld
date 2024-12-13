from typing import Generator

import pytest

import cmipld.api.universe as universe
from cmipld.api import SearchSettings, SearchType

_SOME_DATA_DESCRIPTOR_IDS = ['institution', 'product', 'variable']
_SOME_TERM_IDS = ['ipsl', 'observations', 'airmass']
_SETTINGS = SearchSettings(type=SearchType.LIKE)


def _provide_data_descriptor_ids() -> Generator:
    for id in _SOME_DATA_DESCRIPTOR_IDS:
        yield id


@pytest.fixture(params=_provide_data_descriptor_ids())
def data_descriptor_id(request) -> str:
    return request.param


def _provide_term_ids() -> Generator:
    for id in _SOME_TERM_IDS:
        yield id


@pytest.fixture(params=_provide_term_ids())
def term_id(request) -> str:
    return request.param


def test_get_all_terms_in_universe() -> None:
    universe.get_all_terms_in_universe()


def test_get_all_data_descriptors_in_universe() -> None:
    universe.get_all_data_descriptors_in_universe()


def test_get_terms_in_data_descriptor(data_descriptor_id) -> None:
    universe.get_all_terms_in_data_descriptor(data_descriptor_id)
        

def test_find_term_in_data_descriptor(data_descriptor_id, term_id) -> None:
    universe.find_terms_in_data_descriptor(data_descriptor_id, term_id)
    universe.find_terms_in_data_descriptor(data_descriptor_id, term_id, _SETTINGS)


def test_find_terms_in_universe(term_id) -> None:
    universe.find_terms_in_universe(term_id)
    universe.find_terms_in_universe(term_id, settings=_SETTINGS)


def test_find_data_descriptor_in_universe(data_descriptor_id) -> None:
    universe.find_data_descriptors_in_universe(data_descriptor_id)
    universe.find_data_descriptors_in_universe(data_descriptor_id, settings=_SETTINGS)    