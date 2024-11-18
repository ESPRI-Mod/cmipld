from cmipld.models.table import Table 
from cmipld.models.activity import Activity
from cmipld.models.consortia import Consortia
from cmipld.models.experiment import Experiment 
from cmipld.models.forcing_index import ForcingIndex
from cmipld.models.frequency import Frequency
from cmipld.models.grid_label import GridLabel 
from cmipld.models.initialisation_index import InitialisationIndex 
from cmipld.models.institution import Institution
from cmipld.models.license import License 
from cmipld.models.mip_era import MipEra
from cmipld.models.model_component import ModelComponent
from cmipld.models.organisation import Organisation 
from cmipld.models.physic_index import PhysicIndex
from cmipld.models.product import Product
from cmipld.models.realisation_index import RealisationIndex 
from cmipld.models.realm import Realm
from cmipld.models.resolution import Resolution
from cmipld.models.source import Source 
from cmipld.models.source_type import SourceType 
from cmipld.models.sub_experiment import SubExperiment
from cmipld.models.variable import Variable
from cmipld.models.variant_label import VariantLabel
from cmipld.models.time_range import TimeRange


mapping = {
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
    "time_range": TimeRange
    "variable": Variable,
    "variant_label": VariantLabel
}