from pathlib import Path
import json

def read_json_file(json_file_path: Path) -> dict:
    return json.loads(json_file_path.read_text())