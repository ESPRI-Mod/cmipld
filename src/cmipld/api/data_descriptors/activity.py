
from __future__ import annotations 
from typing import (
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



class Activity(ConfiguredBaseModel):
    """
    an 'activity' refers to a coordinated set of modeling experiments designed to address specific scientific questions or objectives. Each activity is focused on different aspects of climate science and utilizes various models to study a wide range of climate phenomena. Activities are often organized around key research themes and may involve multiple experiments, scenarios, and model configurations.
    """

    id: str 
    validation_method: str = Field(default = "list")
    name: str 
    long_name: str 
    cmip_acronym: str 
    url: Optional[str] 


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Activity.model_rebuild()
