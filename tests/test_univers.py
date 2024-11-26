import cmipld.api.univers as univers

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
    for item in _SOME_TERM_REQUESTS:
        univers.find_term_in_data_descriptor(**item)


def test_find_terms_in_univers() -> None:
    for term_id in _SOME_TERM_IDS:
        univers.find_terms_in_univers(term_id)


def test_find_data_descriptor_in_univers() -> None:
    for data_descriptor_id in _SOME_DATA_DESCRIPTOR_IDS:
        univers.find_data_descriptors_in_univers(data_descriptor_id)