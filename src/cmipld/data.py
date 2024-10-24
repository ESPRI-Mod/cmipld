from typing import LiteralString
import requests
from pyld import jsonld
from dataclasses import dataclass
import urllib3
urllib3.disable_warnings()
import json,os
def local_document_loader(local_path, options=None):
    def loader(local_path, options=None):
        
        if local_path[0]==".":
            local_path = os.path.abspath(local_path)

        with open(local_path,"r") as f:
            content = json.load(f)
        res ={
            'contextUrl': None,  # No special context URL
            'documentUrl': local_path,  # The document's actual URL
            'document': content  # The parsed JSON-LD document
        }
        #print(res)
        return res
    return loader

@dataclass
class Data():
    
    uri: str # url
    json : dict | None # None if fetch doesn't get response from uri
    expanded : dict # the json expanded with context thanks to pyld
    normalized : LiteralString | dict

    def __init__(self,uri,local_path=None):
        if local_path is not None:
            self.local_path = os.path.abspath(local_path) + "/"
        else:
            self.local_path=None


        self.uri = uri
        self._class_vars = { # lazy loading => load those only if ask for it
            "json": None,
            "expanded" : None,
            "normalized" : None,
        }
        if local_path:
            jsonld.set_document_loader(local_document_loader(""))
        
    
    def _initialize_var(self,var_name): 
        if var_name == "json":
            if self.local_path:
                with open(self.uri,"r") as f:
                    return json.load(f)
            else:
                return self.fetch(self.uri)
        elif var_name == "expanded":
            print("COUCOU", self.local_path, self.uri)
            return jsonld.expand(self.uri,options={"base":self.uri})

        elif var_name == "normalized":
            return jsonld.normalize(self.uri, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
        return None



    def __getattr__(self, name):
        if name in self._class_vars:
            if self._class_vars[name] is None:
                # Initialize the variable the first time it's accessed
                self._class_vars[name] = self._initialize_var(name)
            return self._class_vars[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __str__(self):
        res = "# "*50
        res += "\n"+"# "*20 + f"   {self.uri.split("/")[-1]}   "+"# "*20 +"\n"
        res += "# "*50
        res += f"\nuri : {self.uri}\n"
        res += f"\njson version :\n {self.json}"
        res += f"\n\nexpanded version :\n {self.expanded}"
        res += f"\n\nnormalized version :\n {self.normalized}"

        return res 

    def fetch(self,uri) -> dict | None:
        try:
            print(uri)
            # Make a GET request to the API endpoint using requests.get()
            response = requests.get(uri, headers = {'accept': 'application/json'}, verify=False)
            

            # Check if the request waµs successful (status code 200)
            if response.status_code == 200:
                posts = response.json()
                return posts
            else:
                
                print('Error:', response.status_code)
                return None
            
        except Exception as e:
            print(e) 

            
