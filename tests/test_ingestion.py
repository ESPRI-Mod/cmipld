from pathlib import Path

import pytest

import cmipld.models.sqlmodel.univers as univers
import cmipld.fixtures.univers_ingestion as univers_ingestion
import cmipld.models.sqlmodel.project as project
import cmipld.fixtures.project_ingestion as project_ingestion
import cmipld.db as db
import cmipld.utils.settings as settings


@pytest.fixture(scope="module", autouse=True)
def delete_db():
    univers_file_path = Path(settings.UNIVERS_DB_FILENAME)
    cmip6plus_file_path = Path(db._CMIP6PLUS_FILENAME)
    if univers_file_path.exists():
        univers_file_path.unlink()
    if cmip6plus_file_path.exists():
        cmip6plus_file_path.unlink()


def test_create_univers_db() -> None:
    univers.univers_create_db()


def test_univers_ingestion() -> None:
    univers_ingestion.ingest_all(settings.UNIVERS_DIR_PATH)


def test_create_project_db() -> None:
    project.project_create_db()
    

def test_project_ingestion() -> None:
    project_ingestion.ingest_all(settings.CMIP6PLUS_DIR_PATH)