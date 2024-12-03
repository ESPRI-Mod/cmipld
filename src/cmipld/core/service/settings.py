
from pydantic import BaseModel, Field
from typing import List, Optional
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
    projects: List[ProjectSettings] = Field(default_factory=list)

    @classmethod
    def load_from_file(cls, file_path: str) -> "ServiceSettings":
        """
        Load service settings from a TOML file.
        """
        data = toml.load(file_path)
        return cls.model_validate(data)

    def save_to_file(self, file_path: str):
        """
        Save service settings to a TOML file.
        """
        with open(file_path, "w") as f:
            toml.dump(self.model_dump_json(), f)

