from pydantic import BaseModel

from cmipld.models.data_descriptors.table import Table 
from cmipld.models.data_descriptors.activity import Activity
from cmipld.models.data_descriptors.consortia import Consortia
from cmipld.models.data_descriptors.date import Date
from cmipld.models.data_descriptors.experiment import Experiment 
from cmipld.models.data_descriptors.forcing_index import ForcingIndex
from cmipld.models.data_descriptors.frequency import Frequency
from cmipld.models.data_descriptors.grid_label import GridLabel 
from cmipld.models.data_descriptors.initialisation_index import InitialisationIndex 
from cmipld.models.data_descriptors.institution import Institution
from cmipld.models.data_descriptors.license import License 
from cmipld.models.data_descriptors.mip_era import MipEra
from cmipld.models.data_descriptors.model_component import ModelComponent
from cmipld.models.data_descriptors.organisation import Organisation 
from cmipld.models.data_descriptors.physic_index import PhysicIndex
from cmipld.models.data_descriptors.product import Product
from cmipld.models.data_descriptors.realisation_index import RealisationIndex 
from cmipld.models.data_descriptors.realm import Realm
from cmipld.models.data_descriptors.resolution import Resolution
from cmipld.models.data_descriptors.source import Source 
from cmipld.models.data_descriptors.source_type import SourceType 
from cmipld.models.data_descriptors.sub_experiment import SubExperiment
from cmipld.models.data_descriptors.time_range import TimeRange 
from cmipld.models.data_descriptors.variable import Variable
from cmipld.models.data_descriptors.variant_label import VariantLabel


DATA_DESCRIPTOR_CLASS_MAPPING: dict[str, type[BaseModel]] = {
    "activity": Activity,
    "consortia": Consortia,
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