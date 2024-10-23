from cmipld import settings
from cmipld import model_mapping
from cmipld.data import Data
import os

class CV():
    def __init__(self,local_path=None):
        if local_path:
            self.local = True
            self.url = os.path.abspath(local_path) +"/"
        else:
            self.local = False

            self.url = settings.URL_UNIVERSE

    def get_terms(self,datadescriptor):
        data =  Data(self.url+datadescriptor+".json", local_path=self.url if self.local else None)
        terms_data =  [Data(term["@id"]) for term in data.expanded[self.url+datadescriptor+"/terms"]]
        model = model_mapping[datadescriptor]
        terms = [ model(**elem.json) for elem in terms_data ] 
        return  terms

    def get_term(self, datadescriptor_id, term_id):
        data = Data(self.url+datadescriptor_id+"/"+term_id+".json", local_path=self.url if self.local else None)
        model = model_mapping[datadescriptor_id]
        print(data)
        return model(**data.json)

    def parse_datadescriptor_term(self,datadescriptor_name):

        pass 


    

