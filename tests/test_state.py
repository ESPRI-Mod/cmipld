
import pytest
from unittest.mock import MagicMock
from esgvoc.core.service.state import StateService
from esgvoc.core.service.settings import ServiceSettings, UniverseSettings, ProjectSettings

@pytest.fixture
def mock_repo_fetcher(mocker):
    """Fixture to mock the RepoFetcher class and its methods."""
    mock_rf = mocker.patch('esgvoc.core.repo_fetcher.RepoFetcher')
    instance = mock_rf.return_value
    instance.get_github_version = MagicMock()
    instance.get_local_repo_version = MagicMock()
    instance.clone_repository = MagicMock(return_value=True)
    return instance

@pytest.fixture
def service_settings():
    """Fixture to provide mock service settings."""
    return ServiceSettings(
        universe=UniverseSettings(
            github_repo="https://github.com/example/universe",
            branch="main",
            local_path="/local/universe",
            db_name="universe.db"
        ),
        projects={"Project1":
            ProjectSettings(
                project_name="Project1",
                github_repo="https://github.com/example/project1",
                branch="main",
                local_path="/local/project1",
                db_name="project1.db"
            )

        }
    )

def test_all_in_sync(mock_repo_fetcher, service_settings):
    """Test when all versions are in sync (GitHub, local, and DB)."""
    # Set return values for the mock methods
    mock_repo_fetcher.get_github_version.side_effect = lambda owner, repo, branch: "commit_hash"
    mock_repo_fetcher.get_local_repo_version.side_effect = lambda path, branch: "commit_hash"

    # Initialize StateService
    state_service = StateService(service_settings)

    # Inject the mock RepoFetcher into universe and projects
    state_service.universe.rf = mock_repo_fetcher
    for _, project in state_service.projects.items():
        project.rf = mock_repo_fetcher

    # Get state summary and assert
    summary = state_service.get_state_summary()
    print(summary)

    assert summary['universe']['github_local_sync'] is True
    for project_name,_ in summary['projects'].items():
        assert summary['projects'][project_name]['github_local_sync'] is True



def test_github_ahead_of_local(mock_repo_fetcher, service_settings):
    """Test when GitHub version is ahead of the local version (requires sync)."""
    mock_repo_fetcher.get_github_version.side_effect = lambda owner, repo, branch: "new_commit_hash"
    mock_repo_fetcher.get_local_repo_version.side_effect = lambda path, branch: "old_commit_hash"

    state_service = StateService(service_settings)
# Inject the mock RepoFetcher into universe and projects
    state_service.universe.rf = mock_repo_fetcher
    for _,project in state_service.projects.items():
        project.rf = mock_repo_fetcher


    summary = state_service.get_state_summary()

    assert summary['universe']['github_local_sync'] is False

    # Perform synchronization
    state_service.synchronize_all()
    mock_repo_fetcher.clone_repository.assert_called()

def test_missing_local_repo(mock_repo_fetcher, service_settings):
    """Test when the local repository is missing or inaccessible."""
    mock_repo_fetcher.get_local_repo_version.side_effect = Exception("Local repo not found")

    state_service = StateService(service_settings)
    summary = state_service.get_state_summary()

    assert summary['universe']['github_local_sync'] is None


#TODO when DB will be up

# def test_local_and_db_out_of_sync(mock_repo_fetcher, service_settings):
#     """Test when the local version is ahead of the database."""
#     mock_repo_fetcher.get_github_version.side_effect = lambda owner, repo, branch: "commit_hash"
#     mock_repo_fetcher.get_local_repo_version.side_effect = lambda path, branch: "commit_hash"
#
#     state_service = StateService(service_settings)
#     state_service.universe.db_version = "old_db_hash"  # Simulating an outdated DB version
#
#     summary = state_service.get_state_summary()
#
#     assert summary['universe']['local_db_sync'] is False
