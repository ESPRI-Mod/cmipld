from pydantic import BaseModel, ConfigDict

class GenericTerm(BaseModel):
    id: str
    type: str
    model_config = ConfigDict(extra = "allow")


class GenericPlainTerm(GenericTerm):
    drs_name: str
    

class GenericTermPattern(GenericTerm):
    regex: str


class CompositePart(BaseModel):
    id: str
    type: str
    is_required: bool


class GenericTermComposite(GenericTerm):
    separator: str
    parts: list[CompositePart]