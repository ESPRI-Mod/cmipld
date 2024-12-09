import cmipld.api.univers as univers
from cmipld.api import SearchSettings, SearchType

_SOME_DATA_DESCRIPTOR_IDS = ['institution', 'product', 'variable']
_SOME_TERM_IDS = ['ipsl', 'day']
_SOME_TERM_REQUESTS = [
                          {'data_descriptor_id': 'institution', 'term_id': 'ipsl'},
                          {'data_descriptor_id': 'product', 'term_id': 'observations'},
                          {'data_descriptor_id': 'variable', 'term_id': 'airmass'}
                      ]


def test_get_all_terms_in_univers() -> None:
    univers.get_all_terms_in_univers()


def test_get_all_data_descriptors_in_univers() -> None:
    univers.get_all_data_descriptors_in_univers()


def test_get_terms_in_data_descriptor() -> None:
    for data_descriptor_id in _SOME_DATA_DESCRIPTOR_IDS:
        univers.get_all_terms_in_data_descriptor(data_descriptor_id)


def test_find_term_in_data_descriptor() -> None:
    settings = SearchSettings(type=SearchType.LIKE)
    for item in _SOME_TERM_REQUESTS:
        univers.find_terms_in_data_descriptor(**item)
        univers.find_terms_in_data_descriptor(**item, settings=settings)


def test_find_terms_in_univers() -> None:
    settings = SearchSettings(type=SearchType.LIKE)
    for term_id in _SOME_TERM_IDS:
        univers.find_terms_in_univers(term_id)
        univers.find_terms_in_univers(term_id, settings=settings)


def test_find_data_descriptor_in_univers() -> None:
    settings = SearchSettings(type=SearchType.LIKE)
    for data_descriptor_id in _SOME_DATA_DESCRIPTOR_IDS:
        univers.find_data_descriptors_in_univers(data_descriptor_id)
        univers.find_data_descriptors_in_univers(data_descriptor_id, settings=settings)