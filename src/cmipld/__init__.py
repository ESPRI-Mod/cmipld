from cmipld.api.models import Term

from cmipld.api.data_descriptors import DATA_DESCRIPTOR_CLASS_MAPPING


def get_pydantic_class(data_descriptor_id_or_term_type: str) -> type[Term]:
    if data_descriptor_id_or_term_type in DATA_DESCRIPTOR_CLASS_MAPPING:
        return DATA_DESCRIPTOR_CLASS_MAPPING[data_descriptor_id_or_term_type]
    else:
        raise ValueError(f"{data_descriptor_id_or_term_type} pydantic class not found")