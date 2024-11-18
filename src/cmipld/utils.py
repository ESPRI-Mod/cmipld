from pathlib import Path
import json
import cmipld.settings as settings

def read_json_file(json_file_path: Path) -> dict:
    return json.loads(json_file_path.read_text())
    

def from_pydantic_module_filepath_to_pydantic_class_name(file_path: Path) -> str:
    splits = file_path.stem.split(settings.DIRNAME_AND_FILENAME_SEPARATOR)
    return "".join([split.capitalize() for split in splits])
