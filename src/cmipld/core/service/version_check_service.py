from cmipld.core.repo_fetcher import RepoFetcher
#from .db_service import DBService



class VersionCheckService:
    def __init__(self):
        self.repo_fetcher = RepoFetcher()
        #self.db_service = DBService()

    def check_and_update(self, repo_name: str):
        # Split the repo_name into owner/repo if necessary
        owner, repo = repo_name.split("/", 1)  # Assumes repo_name is in the format "owner/repo"

        # Check DB for repository version
        # db_version = self.db_service.get_version(repo_name)

        # Check if local repository exists and get its version
        local_version = self.repo_fetcher.get_local_repo_version(repo)

        # Get the GitHub version
        github_version = self.repo_fetcher.get_github_version(owner, repo)
        print(local_version)
        print(github_version) 
        print(local_version==github_version)

        # Compare versions and decide what action to take
        # if db_version != local_version or db_version != github_version:
        #     # Repository is outdated, clone and rebuild DB
        #     #self.clone_service.clone_repository(repo_name)
        #     self.db_service.rebuild_db(repo_name)
        #     return f"Repository {repo_name} is updated."
        # else:
        #     return f"Repository {repo_name} is up-to-date."

if __name__ == "__main__":
    vcs = VersionCheckService()
    vcs.check_and_update("ESPRI-Mod/CMIP6Plus_CVs")

