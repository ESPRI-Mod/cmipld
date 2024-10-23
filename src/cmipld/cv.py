from cmipld import settings
from cmipld import model_mapping
from cmipld.data import Data

class CV():
    def __init__(self):
        self.url = settings.URL_UNIVERSE

    def get_terms(self,datadescriptor):
        data =  Data(self.url+datadescriptor+".json")
        terms_data =  [Data(term["@id"]) for term in data.expanded[0][self.url+datadescriptor+"/terms"]]
        #print(terms_data)
        model = model_mapping[datadescriptor]
        terms = [ model(**elem.json) for elem in terms_data ] 
        return  terms

    def get_term(self, datadescriptor_id, term_id):
        data = Data(self.url+datadescriptor_id+"/"+term_id)
        model = model_mapping[datadescriptor_id]
        print(data.normalized)
        return model(**data.json)

    def parse_datadescriptor_term(self,datadescriptor_name):

        pass 


    

