import os
from pathlib import Path

import cmipld.models.sqlmodel.univers as univers

_THIS_FILE_PATH = Path(os.path.abspath(__file__))

def test_create_univers_db() -> None:
    univers.univers_create_db()
    
