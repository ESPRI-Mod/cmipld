from cmipld.core.data_fetcher import DataFetcher
#from .db_service import DBService

class VersionCheckService:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.db_service = DBService()

    def check_and_update(self, repo_name: str):
        # Split the repo_name into owner/repo if necessary
        owner, repo = repo_name.split("/", 1)  # Assumes repo_name is in the format "owner/repo"

        # Check DB for repository version
        db_version = self.db_service.get_version(repo_name)

        # Check if local repository exists and get its version
        local_version = self.data_fetcher.get_local_repo_version(repo_name)

        # Get the GitHub version
        github_version = self.data_fetcher.get_github_version(owner, repo)

        # Compare versions and decide what action to take
        if db_version != local_version or db_version != github_version:
            # Repository is outdated, clone and rebuild DB
            #self.clone_service.clone_repository(repo_name)
            self.db_service.rebuild_db(repo_name)
            return f"Repository {repo_name} is updated."
        else:
            return f"Repository {repo_name} is up-to-date."
