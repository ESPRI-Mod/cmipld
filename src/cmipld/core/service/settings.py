
from pydantic import BaseModel, Field
from typing import Dict, Optional
import toml



class ProjectSettings(BaseModel):
    project_name: str
    github_repo: str
    branch :Optional[str] = "main"
    local_path: Optional[str] = None
    db_name: Optional[str] = None

class UniverseSettings(BaseModel):
    github_repo: str
    branch : Optional[str] = None
    local_path: Optional[str] = None
    db_name: Optional[str] = None

class ServiceSettings(BaseModel):
    universe: UniverseSettings
    projects: Dict[str,ProjectSettings] = Field(default_factory=dict)

    # Custom validation to convert a list to a dictionary, if needed
    @classmethod
    def from_projects_list(cls, universe: UniverseSettings, projects_list: list[ProjectSettings]):
        return cls(
            universe=universe,
            projects={project["project_name"]: project for project in projects_list}
        )

    @classmethod
    def load_from_file(cls, file_path: str) -> "ServiceSettings":
        """
        Load service settings from a TOML file.
        """
        data = toml.load(file_path) 
        return cls.from_projects_list(data["universe"],data["projects"])

    def save_to_file(self, file_path: str):
        """
        Save service settings to a TOML file.
        """
        project_list = []
        for project_name in self.projects.keys():
            project_list.append(self.projects[project_name].model_dump())

        data = {}
        data["projects"] = project_list
        data["universe"] = self.universe.model_dump()

        with open(file_path, "w") as f:
            toml.dump(data, f)
        
        
