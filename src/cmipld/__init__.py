from pydantic import BaseModel

from cmipld.api.data_descriptors import DATA_DESCRIPTOR_CLASS_MAPPING


def get_pydantic_class(data_descriptor_id: str) -> type[BaseModel]:
    if data_descriptor_id in DATA_DESCRIPTOR_CLASS_MAPPING:
        return DATA_DESCRIPTOR_CLASS_MAPPING[data_descriptor_id]
    else:
        raise ValueError(f"{data_descriptor_id} pydantic class not found")