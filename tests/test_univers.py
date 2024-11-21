import cmipld.univers as univers

_DATA_DESCRIPTOR_IDS = ['institution', 'product', 'variable']
_TERM_REQUESTS = [
                     {'data_descriptor_id': 'institution', 'term_id': 'ipsl'},
                     {'data_descriptor_id': 'product', 'term_id': 'observations'},
                     {'data_descriptor_id': 'variable', 'term_id': 'airmass'}
                 ]


def test_get_all_terms() -> None:
    univers.get_all_terms()


def test_get_all_data_descriptors() -> None:
    univers.get_all_data_descriptors()


def test_get_terms() -> None:
    for data_descriptor_id in _DATA_DESCRIPTOR_IDS:
        univers.get_terms(data_descriptor_id)


def test_get_term() -> None:
    for item in _TERM_REQUESTS:
        univers.get_term(**item)