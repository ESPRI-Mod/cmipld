
from __future__ import annotations 
from typing import (
    List,
    Optional,
    Union
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


class Dates(ConfiguredBaseModel):

    phase : str
    from_ : int = Field(...,alias="from") # cause from is a keyword
    to: Union[int,str]
    

class Member(ConfiguredBaseModel):
    
    type : str
    institution : str # id 
    dates : List[Dates] = Field(default_factory=list)
    membership_type : str # prior, current

class Consortium(ConfiguredBaseModel):

    id: str 
    validation_method: str = Field(default = "list")
    type: str
    name: Optional[str] = None 
    cmip_acronym: str = Field(...,alias="cmip-acronym") 
    status : Optional[str] = None
    changes : Optional[str]
    members : List[Member] = Field(default_factory=list)
    url: Optional[str] 


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Consortium.model_rebuild()
