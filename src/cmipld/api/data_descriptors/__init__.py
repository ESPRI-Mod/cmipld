from pydantic import BaseModel

from cmipld.api.data_descriptors.activity import Activity
from cmipld.api.data_descriptors.consortium import Consortium
from cmipld.api.data_descriptors.date import Date
from cmipld.api.data_descriptors.experiment import Experiment 
from cmipld.api.data_descriptors.forcing_index import ForcingIndex
from cmipld.api.data_descriptors.frequency import Frequency
from cmipld.api.data_descriptors.grid_label import GridLabel 
from cmipld.api.data_descriptors.initialisation_index import InitialisationIndex 
from cmipld.api.data_descriptors.institution import Institution
from cmipld.api.data_descriptors.license import License 
from cmipld.api.data_descriptors.mip_era import MipEra
from cmipld.api.data_descriptors.model_component import ModelComponent
from cmipld.api.data_descriptors.organisation import Organisation 
from cmipld.api.data_descriptors.physic_index import PhysicIndex
from cmipld.api.data_descriptors.product import Product
from cmipld.api.data_descriptors.realisation_index import RealisationIndex 
from cmipld.api.data_descriptors.realm import Realm
from cmipld.api.data_descriptors.resolution import Resolution
from cmipld.api.data_descriptors.source import Source 
from cmipld.api.data_descriptors.source_type import SourceType 
from cmipld.api.data_descriptors.sub_experiment import SubExperiment
from cmipld.api.data_descriptors.table import Table 
from cmipld.api.data_descriptors.time_range import TimeRange 
from cmipld.api.data_descriptors.variable import Variable
from cmipld.api.data_descriptors.variant_label import VariantLabel


DATA_DESCRIPTOR_CLASS_MAPPING: dict[str, type[BaseModel]] = {
    "activity": Activity,
    "consortium": Consortium,
    "date": Date,
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
