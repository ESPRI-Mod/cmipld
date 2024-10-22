from cmipld import settings
from cmipld import model_mapping
from pyld import jsonld
from cmipld.core import Data
class CV():
    def __init__(self):
        self.url = settings.URL_UNIVERSE

    def parse_datadescriptor(self,datadescriptor):
        data =  Data(self.url+datadescriptor+".json")
        terms_data =  [Data(term["@id"]) for term in data.expanded[0][self.url+datadescriptor+"/terms"]]
        #print(terms_data)
        model = model_mapping[datadescriptor]
        terms = [ model(**elem.json) for elem in terms_data ] 
        return  terms

    def parse_datadescriptor_term(self,datadescriptor_name):

        pass 


    

