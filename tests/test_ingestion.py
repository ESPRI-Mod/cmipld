from pathlib import Path

import pytest

import cmipld.models.sqlmodel.univers as univers
import cmipld.fixtures.univers_ingestion as univers_ingestion
import cmipld.models.sqlmodel.project as project
import cmipld.fixtures.project_ingestion as project_ingestion
import cmipld.db as db


@pytest.fixture(scope="module", autouse=True)
def delete_db():
    univers_file_path = Path(db.UNIVERS_DB_FILE_PATH)
    cmip6plus_file_path = Path(db.CMIP6PLUS_DB_FILE_PATH)
    if univers_file_path.exists():
        univers_file_path.unlink()
    if cmip6plus_file_path.exists():
        cmip6plus_file_path.unlink()


def test_create_univers_db() -> None:
    univers.univers_create_db(db.UNIVERS_DB_FILE_PATH)


def test_univers_ingestion(caplog) -> None:
    caplog.clear()
    univers_ingestion.ingest_univers(db.UNIVERS_DIR_PATH, db.UNIVERS_DB_FILE_PATH)
    count_error_tags = caplog.text.count("ERROR")
    assert count_error_tags == 0


def test_create_project_db() -> None:
    project.project_create_db(db.CMIP6PLUS_DB_FILE_PATH)
    

def test_project_ingestion(caplog) -> None:
    caplog.clear()
    project_ingestion.ingest_project(db.CMIP6PLUS_DIR_PATH,
                                     db.CMIP6PLUS_DB_FILE_PATH,
                                     db.UNIVERS_DB_FILE_PATH)
    count_error_tags = caplog.text.count("ERROR")
    assert count_error_tags == 0