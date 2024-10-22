
from __future__ import annotations 
from datetime import (
    datetime,
    date
)
from decimal import Decimal 
from enum import Enum 
import re
import sys
from typing import (
    Any,
    ClassVar,
    List,
    Literal,
    Dict,
    Optional,
    Union
)
from pydantic.version import VERSION  as PYDANTIC_VERSION 
if int(PYDANTIC_VERSION[0])>=2:
    from pydantic import (
        BaseModel,
        ConfigDict,
        Field,
        RootModel,
        field_validator
    )
else:
    from pydantic import (
        BaseModel,
        Field,
        validator
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
