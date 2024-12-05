from pydantic import BaseModel, Field
from typing import Dict, Optional
import toml

class ProjectSettings(BaseModel):
    project_name: str
    github_repo: str
    branch: Optional[str] = "main"
    local_path: Optional[str] = None
    db_name: Optional[str] = None

class UniverseSettings(BaseModel):
    github_repo: str
    branch: Optional[str] = None
    local_path: Optional[str] = None
    db_name: Optional[str] = None

class ServiceSettings(BaseModel):
    universe: UniverseSettings
    projects: Dict[str, ProjectSettings] = Field(default_factory=dict)

    @classmethod
    def load_from_file(cls, file_path: str) -> "ServiceSettings":
        data = toml.load(file_path)
        projects = {p['project_name']: ProjectSettings(**p) for p in data.pop('projects', [])}
        return cls(universe=UniverseSettings(**data['universe']), projects=projects)

    def save_to_file(self, file_path: str):
        data = {
            "universe": self.universe.model_dump(),
            "projects": [p.model_dump() for p in self.projects.values()]
        }
        with open(file_path, "w") as f:
            toml.dump(data, f)
