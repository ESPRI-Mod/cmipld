from pydantic import BaseModel

from cmipld.models.pydantic.table import Table 
from cmipld.models.pydantic.activity import Activity
from cmipld.models.pydantic.consortia import Consortia
from cmipld.models.pydantic.experiment import Experiment 
from cmipld.models.pydantic.forcing_index import ForcingIndex
from cmipld.models.pydantic.frequency import Frequency
from cmipld.models.pydantic.grid_label import GridLabel 
from cmipld.models.pydantic.initialisation_index import InitialisationIndex 
from cmipld.models.pydantic.institution import Institution
from cmipld.models.pydantic.license import License 
from cmipld.models.pydantic.mip_era import MipEra
from cmipld.models.pydantic.model_component import ModelComponent
from cmipld.models.pydantic.organisation import Organisation 
from cmipld.models.pydantic.physic_index import PhysicIndex
from cmipld.models.pydantic.product import Product
from cmipld.models.pydantic.realisation_index import RealisationIndex 
from cmipld.models.pydantic.realm import Realm
from cmipld.models.pydantic.resolution import Resolution
from cmipld.models.pydantic.source import Source 
from cmipld.models.pydantic.source_type import SourceType 
from cmipld.models.pydantic.sub_experiment import SubExperiment
from cmipld.models.pydantic.time_range import TimeRange 
from cmipld.models.pydantic.variable import Variable
from cmipld.models.pydantic.variant_label import VariantLabel


DATA_DESCRIPTOR_CLASS_MAPPING: dict[str, type[BaseModel]] = {
    "activity": Activity,
    "consortia": Consortia,
    "experiment": Experiment, 
    "forcing_index": ForcingIndex,
    "frequency": Frequency,
    "grid": GridLabel, 
    "initialisation_index": InitialisationIndex, 
    "institution": Institution,
    "license": License,
    "mip_era": MipEra,
    "model_component": ModelComponent,
    "organisation": Organisation, 
    "physic_index": PhysicIndex,
    "product": Product,
    "realisation_index": RealisationIndex ,
    "realm": Realm,
    "resolution": Resolution,
    "source": Source, 
    "source_type": SourceType, 
    "sub_experiment": SubExperiment,
    "table" : Table,
    "time_range": TimeRange,
    "variable": Variable,
    "variant_label": VariantLabel
}