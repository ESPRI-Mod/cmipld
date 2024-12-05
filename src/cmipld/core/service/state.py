import logging
from typing import Optional
from cmipld.core.repo_fetcher import RepoFetcher
from cmipld.core.service.settings import UniverseSettings, ProjectSettings, ServiceSettings 

logger = logging.getLogger(__name__)

class BaseState:
    def __init__(self, github_repo: str, branch: str = "main", local_path: Optional[str] = None, db_name: Optional[str] = None):
        self.github_repo = github_repo
        self.branch = branch
        self.local_path = local_path
        self.db_name = db_name
        self.github_version = None
        self.local_version = None
        self.db_version = None
        self.rf = RepoFetcher()

    def fetch_versions(self):
        try:
            owner, repo = self.github_repo.lstrip("https://github.com/").split("/")
            self.github_version = self.rf.get_github_version(owner, repo, self.branch)
            logger.info(f"Latest GitHub commit: {self.github_version}")
        except Exception as e:
            logger.exception(f"Failed to fetch GitHub version: {e}")

        if self.local_path:
            try:
                self.local_version = self.rf.get_local_repo_version(self.local_path, self.branch)
                logger.info(f"Local repo commit: {self.local_version}")
            except Exception as e:
                logger.exception(f"Failed to fetch local repo version: {e}")

    def check_sync_status(self):
        self.fetch_versions()
        return {
            "github_sync": self.github_version == self.local_version if self.github_version and self.local_version else None,
            "local_db_sync": self.local_version == self.db_version if self.local_version and self.db_version else None,
            "github_db_sync": self.github_version == self.db_version if self.github_version and self.db_version else None
        }

    def sync(self):
        if self.github_version and self.github_version != self.local_version:
            owner, repo = self.github_repo.lstrip("https://github.com/").split("/")
            self.rf.clone_repository(owner, repo, self.branch)
            self.fetch_versions()

class StateUniverse(BaseState):
    def __init__(self, settings: UniverseSettings):
        super().__init__(**settings.model_dump())

class StateProject(BaseState):
    def __init__(self, settings: ProjectSettings):
        mdict = settings.model_dump()
        self.project_name = mdict.pop("project_name")
        super().__init__(**mdict)
        

class StateService:
    def __init__(self, service_settings: ServiceSettings):
        self.universe = StateUniverse(service_settings.universe)
        self.projects = {name: StateProject(proj) for name, proj in service_settings.projects.items()}

    def get_state_summary(self):
        universe_status = self.universe.check_sync_status()
        project_statuses = {name: proj.check_sync_status() for name, proj in self.projects.items()}
        return {"universe": universe_status, "projects": project_statuses}

    def synchronize_all(self):
        self.universe.sync()
        for project in self.projects.values():
            project.sync()
    # def find_version_differences(self):
    #     summary = self.get_state_summary()
    #     if not summary["universe"]["github_sync"]:
    #         print("OUT OF SYNC")
    #         print(f"github universe version: {self.universe.github_version}")
    #         print(f"local universe version: {self.universe.local_version}")
    #     for project in summary["projects"]:
    #         if not project["github_sync"]:
    #             print("OUT OF SYNC")
    #             print("AHHHHHHHHHHHH", project)
    #             # print(f"github {project["project_name"]} version: {project["github_version"]}")
    #             # print(f"local {project["project_name"]} version: {project["local_version"]}")
    #
    #     out_of_sync_projects = [
    #         project for project in summary["projects"] if not project["github_db_sync"]
    #     ]
    #     return {
    #         "universe_out_of_sync": not summary["universe"]["github_db_sync"],
    #         "out_of_sync_projects": out_of_sync_projects
    #     }


if __name__ == "__main__":
    from pprint import pprint 
    # Load settings from file
    service_settings = ServiceSettings.load_from_file("src/cmipld/core/service/settings.toml")
    
    # Initialize StateService
    state_service = StateService(service_settings)
    state_service.get_state_summary()

        # Synchronize all
    state_service.synchronize_all()

    pprint(state_service.universe)

    
    # Check for differences
    #pprint(state_service.find_version_differences())
