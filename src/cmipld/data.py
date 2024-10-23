from typing import LiteralString
import requests
from pyld import jsonld
from dataclasses import dataclass
import urllib3
urllib3.disable_warnings()

@dataclass
class Data():
    uri: str # url
    json : dict | None # None if fetch doesn't get response from uri
    expanded : dict # the json expanded with context thanks to pyld
    normalized : LiteralString | dict

    def __init__(self,uri):
        
        self.uri = uri
        self.json = self.fetch(uri)
        self.expanded = jsonld.expand(uri)[0] 
        #print(self.expanded)
        self.normalized = jsonld.normalize(uri, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
        print(type(self.normalized))

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

            
