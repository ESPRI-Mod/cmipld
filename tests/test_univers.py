import cmipld.univers as univers

_DATA_DESCRIPTOR_IDS = ['institution', 'product', 'variable']
_TERM_REQUESTS = [
                     {'data_descriptor_id': 'institution', 'term_id': 'ipsl'},
                     {'data_descriptor_id': 'product', 'term_id': 'observations'},
                     {'data_descriptor_id': 'variable', 'term_id': 'airmass'}
                 ]


def test_get_all_terms_in_univers() -> None:
    univers.get_all_terms_in_univers()


def test_get_all_data_descriptors_in_univers() -> None:
    univers.get_all_data_descriptors_in_univers()


def test_get_terms_in_data_descriptor() -> None:
    for data_descriptor_id in _DATA_DESCRIPTOR_IDS:
        univers.get_all_terms_in_data_descriptor(data_descriptor_id)


def test_get_term_in_data_descriptor() -> None:
    for item in _TERM_REQUESTS:
        univers.get_term_in_data_descriptor(**item)