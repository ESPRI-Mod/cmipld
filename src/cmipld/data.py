from functools import cached_property
from typing import Any
import requests
from pyld import jsonld
from dataclasses import dataclass
import json
import os
from cmipld import model_mapping


def local_document_loader(local_path, options=None):
    def loader(local_path, options=None):
        if local_path[0] == ".":
            local_path = os.path.abspath(local_path)

        with open(local_path, "r") as f:
            content = json.load(f)
        res = {
            "contextUrl": None,  # No special context URL
            "documentUrl": local_path,  # The document's actual URL
            "document": content,  # The parsed JSON-LD document
        }
        # print(res)
        return res

    return loader


@dataclass
class Data:
    uri: str  # url
    local_path: str | None = None

    def __post_init__(self):
        if self.local_path is not None:
            self.local_path = os.path.abspath(self.local_path) + "/"
        else:
            self.local_path = None
        if self.local_path:
            jsonld.set_document_loader(local_document_loader(""))

    @cached_property
    def json(self) -> dict | None:
        if self.local_path:
            with open(self.uri, "r") as f:
                return json.load(f)
        else:
            return self.fetch(self.uri)

    @cached_property
    def expanded(self) -> Any | list[Any]:
        return jsonld.expand(self.uri, options={"base": self.uri})

    @cached_property
    def normalized(self) -> str | dict:
        return jsonld.normalize(
            self.uri, {"algorithm": "URDNA2015", "format": "application/n-quads"}
        )

    @cached_property
    def python(self) -> dict | None:
        model = self.uri.split("/")[-2]
        if model in model_mapping.keys():
            # TODO have to check if [-2] is a valid collection .. or exist in model_mapping
            return model_mapping[model](**self.json)

    @property
    def info(self):
        res = "# " * 50
        res += "\n" + "# " * 20 + f"   {self.uri.split("/")[-1]}   " + "# " * 20 + "\n"
        res += "# " * 50
        res += f"\nuri : {self.uri}\n"
        res += f"\njson version :\n {self.json}"
        res += f"\n\nexpanded version :\n {self.expanded}"
        res += f"\n\nnormalized version :\n {self.normalized}"
        res += f"\n\npython version :\n {self.python}"
        return res

    def fetch(self, uri) -> dict | None:
        try:
            print(uri)
            # Make a GET request to the API endpoint using requests.get()
            response = requests.get(
                uri, headers={"accept": "application/json"}, verify=False
            )

            # Check if the request waµs successful (status code 200)
            if response.status_code == 200:
                posts = response.json()
                return posts
            else:
                print("Error:", response.status_code)
                return None

        except Exception as e:
            print(e)

    # @property
    # def toto(self) -> dict[str, str]:
    #     print("GETTING TOTO")
    #     return {"toto": "toto"}
    #
    # @cached_property
    # def toto2(self) -> dict[str, str]:
    #     print("CACHING TOTO2")
    #     return {"toto": "tot
