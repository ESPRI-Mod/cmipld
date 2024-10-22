import requests
from pyld import jsonld
from dataclasses import dataclass
import urllib3
urllib3.disable_warnings()

@dataclass
class Data():
    uri: str # url
    ressource : str # last part of the uri
    json : dict
    expanded : dict # the json expanded with context thanks to pyld
    uri : str

    def __init__(self,uri):
        self.ressource = uri.split("/")[-1]
        self.json = self.fetch(uri)
        self.expanded = jsonld.expand(uri)   
        self.uri = uri

    def __str__(self):
        res = "# "*50

        res += "\n"+"# "*20 + f"   {self.ressource}   "+"# "*20 +"\n"
        res += "# "*50


        res += f"\nuri : {self.uri}\n"
        res += f"\njson version :\n {self.json}"
        res += f"\n\nexpanded verison :\n {self.expanded}"
        return res 

    def fetch(self,uri):
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

            
