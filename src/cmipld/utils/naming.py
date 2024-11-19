import json
from pathlib import Path


def read_json_file(json_file_path: Path) -> dict:
    return json.loads(json_file_path.read_text())
