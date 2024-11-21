import json
from pathlib import Path
from pydantic import BaseModel
from cmipld.models.pydantic import DATA_DESCRIPTOR_CLASS_MAPPING


def read_json_file(json_file_path: Path) -> dict:
    return json.loads(json_file_path.read_text())


def get_pydantic_class(data_descriptor_id: str) -> type[BaseModel]:
    if data_descriptor_id in DATA_DESCRIPTOR_CLASS_MAPPING:
        return DATA_DESCRIPTOR_CLASS_MAPPING[data_descriptor_id]
    else:
        raise ValueError(f'{data_descriptor_id} pydantic class not found')