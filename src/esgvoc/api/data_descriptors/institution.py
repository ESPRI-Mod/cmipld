

from __future__ import annotations 
from typing import (
    List,
    Dict,
    Optional
)
from pydantic.version import VERSION  as PYDANTIC_VERSION 
if int(PYDANTIC_VERSION[0])>=2:
    from pydantic import (
        BaseModel,
        ConfigDict,
        Field
    )
else:
    from pydantic import (
        BaseModel,
        Field
    )

metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "allow",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass


class Institution(ConfiguredBaseModel):
    
    """
    an registered institution for WCRP modelisation MIP
    """

    
    id: str
    acronyms: List[str] = Field(default_factory=list)
    aliases: Optional[List[str]] = Field(default_factory=list)
    established: Optional[int] 
    type: Optional[str] 
    labels: Optional[List[str]] = Field(default_factory=list)
    location: Optional[Dict] = Field(default_factory=dict)  
    name: str 
    ror: Optional[str] 
    url: Optional[List[str]] = Field(default_factory=list)

# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Institution.model_rebuild()
