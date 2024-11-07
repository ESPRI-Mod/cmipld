from cmipld.data import Data
from cmipld.settings import URL_UNIVERSE 

def test_dummy():
    assert 1==1

def test_data_ipsl_universe():
    a = Data(URL_UNIVERSE + "institution/ipsl.json")
    print(a)
