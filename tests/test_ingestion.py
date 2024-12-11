from pathlib import Path

import pytest

import cmipld.db as db
import cmipld.db.models.project as project
import cmipld.db.models.universe as universe
import cmipld.db.project_ingestion as project_ingestion
import cmipld.db.universe_ingestion as universe_ingestion


# TODO: automate each tests!
@pytest.fixture(scope="module", autouse=True)
def delete_db():
    universe_file_path = Path(db.UNIVERSE_DB_FILE_PATH)
    cmip6plus_file_path = Path(db.CMIP6PLUS_DB_FILE_PATH)
    if universe_file_path.exists():
        universe_file_path.unlink()
    if cmip6plus_file_path.exists():
        cmip6plus_file_path.unlink()


def test_create_universe_db() -> None:
    universe.universe_create_db(db.UNIVERSE_DB_FILE_PATH)


def test_universe_ingestion(caplog) -> None:
    caplog.clear()
    universe_ingestion.ingest_universe(db.UNIVERSE_DIR_PATH, db.UNIVERSE_DB_FILE_PATH)
    count_error_tags = caplog.text.count("ERROR")
    if count_error_tags > 0:
        print(caplog.text)
        raise Exception(f'Found {count_error_tags} error(s)')


def test_create_project_db() -> None:
    project.project_create_db(db.CMIP6PLUS_DB_FILE_PATH)
    

def test_project_ingestion(caplog) -> None:
    caplog.clear()
    project_ingestion.ingest_project(db.CMIP6PLUS_DIR_PATH,
                                     db.CMIP6PLUS_DB_FILE_PATH,
                                     db.UNIVERSE_DB_FILE_PATH)
    count_error_tags = caplog.text.count("ERROR")
    if count_error_tags > 0:
        print(caplog.text)
        raise Exception(f'Found {count_error_tags} error(s)')