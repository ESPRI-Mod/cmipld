from cmipld.core.repo_fetcher import RepoFetcher
from cmipld.core.service.settings import ServiceSettings, UniverseSettings, ProjectSettings
import logging

logger = logging.getLogger(__name__)

from typing import Optional

class BaseState:
    def __init__(self, github_repo: str, branch:str="main", local_path: Optional[str] = None, db_name: Optional[str] = None):
        self.github_repo = github_repo
        self.branch = branch
        self.local_path = local_path
        self.db_name = db_name
        self.github_version = None  # Placeholder, fetched dynamically
        self.local_version = None  # Placeholder, fetched dynamically
        self.db_version = None  # Placeholder, fetched dynamically
        self.rf = RepoFetcher()

    def check_sync_status(self) -> dict:

        try : 
            owner, repo = self.github_repo.lstrip("https://github.com/").split("/")
            branch = self.branch
            self.github_version = self.rf.get_github_version(owner, repo, branch)
            logger.info(f"found {self.github_repo} and the latest commit is {self.github_version}" )
            print(f"found {self.github_repo} and the latest commit is {self.github_version}" )
    

        except Exception as e:
            logger.info("probably, cant find repo and owner from github link in settings.toml" , e)
            print("PROBLEM", e)
            
        try : 
            if self.local_path is not None:
                
                self.local_version = self.rf.get_local_repo_version(self.local_path, self.branch)
                logger.info(f"found {self.local_path} and the latest commit is {self.local_version}" )


        except Exception as e:
            logger.info("Cant find local repository from github link in settings.toml" , e)

        ## TODO Add Get Version from DB ##

        return {
            "github_sync": self.github_version == self.local_version if (self.github_version is not None and self.local_version is not None) else None,
            "local_db_sync": self.local_version == self.db_version if (self.local_version is not None and self.db_version is not None) else None,
            "github_db_sync": self.github_version == self.db_version if (self.github_version is not None and self.db_version is not None) else None
        }

    def sync(self) -> bool:
        # Placeholder sync logic
        # the truth is always the github repository 
        # but if local and distant version are not the same => git pull
        if self.github_version is not None and self.github_version != self.local_version:
            owner, repo = self.github_repo.lstrip("https://github.com/").split("/")
            branch = self.branch
            self.rf.clone_repository(owner,repo, branch)
            self.check_sync_status()    
        
        #TODO add DB sync 
        #self.local_version = self.github_version
        #self.db_version = self.github_version
            
        return True

    def __repr__(self) -> str:
        return (
            f"<BaseState(github_repo={self.github_repo}, local_path={self.local_path}, "
            f"db_name={self.db_name}, github_version={self.github_version}, "
            f"local_version={self.local_version}, db_version={self.db_version})>"
        )


class StateUniverse(BaseState):
    def __init__(self, settings: UniverseSettings):
        super().__init__(settings.github_repo, settings.branch, settings.local_path, settings.db_name)

class StateProject(BaseState):
    def __init__(self, settings: ProjectSettings, project_name: str):
        super().__init__(settings.github_repo,settings.branch, settings.local_path, settings.db_name)
        self.project_name = project_name

    def check_sync_status(self):
        status = super().check_sync_status()
        status["project_name"] = self.project_name
        return status

class StateService:
    def __init__(self, service_settings: ServiceSettings):
        self.universe = StateUniverse(service_settings.universe)
        self.projects = [StateProject(project, project.project_name) for project in service_settings.projects]

    def get_state_summary(self):
        universe_status = self.universe.check_sync_status()
        project_statuses = [project.check_sync_status() for project in self.projects]
        return {"universe": universe_status, "projects": project_statuses}

    def synchronize_all(self):
        self.universe.sync()
        for project in self.projects:
            project.sync()
        return True

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
