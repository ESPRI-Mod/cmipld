from pydantic import BaseModel, ConfigDict

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

class Part(ConfiguredBaseModel):
    id: str
    type : str
    is_required : bool

class TimeRange(ConfiguredBaseModel):
    id: str 
    separator: str 
    type: str 
    parts: list[Part] 


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
TimeRange.model_rebuild()