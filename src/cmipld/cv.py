from cmipld import settings
from cmipld import model_mapping
from cmipld.data import Data
import os

class CMIP6Plus_CV():
    def __init__(self,local_path=None,local_path_universe=None):
        if local_path is None:
            self.url = settings.URL_CMIP6PLUS_CV
            self.local = False
        else:
            self.local = True
            self.url = local_path

        if local_path_universe is None:

            self.local_universe = False
            self.url_universe = settings.URL_UNIVERSE
        else:
            self.local_universe = True
            self.url_universe = local_path_universe
        

    def get_terms(self, collection):
        data=Data(self.url+collection+".json")
        return data

    def get_term(self,collection,term_id):
    
        collection_data = self.get_terms(collection)
        if term_id not in collection_data.json[collection]:
            print("DOESNT EXIST FOR THIS PROJECT")
            return None

        link_universe_datadescriptor = list(collection_data.expanded[0].keys())[0].replace(self.url_universe,"")[:-1]
        data = Data(self.url_universe+link_universe_datadescriptor+"/"+term_id+".json")

        model = model_mapping[link_universe_datadescriptor]

        return model(**data.json)


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
        #print(data)
        terms_data =  [Data(self.url+datadescriptor+"/"+term["@value"]+".json") for term in data.expanded[0][self.url+datadescriptor]]
        model = model_mapping[datadescriptor]
        #print(terms_data)
        terms = [ model(**elem.json) for elem in terms_data ] 
        return  terms

    def get_term(self, datadescriptor_id, term_id):
        data = Data(self.url+datadescriptor_id+"/"+term_id+".json", local_path=self.url if self.local else None)
        model = model_mapping[datadescriptor_id]
        print(data)
        return model(**data.json)

    def parse_datadescriptor_term(self,datadescriptor_name):

        pass 


    

