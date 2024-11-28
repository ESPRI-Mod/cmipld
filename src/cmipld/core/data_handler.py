
import os
import json
import logging
from functools import cached_property
from typing import Any, Optional, Dict
import requests
from pyld import jsonld
from pydantic import BaseModel, model_validator, ConfigDict
import cmipld.db

from cmipld.api.data_descriptors import DATA_DESCRIPTOR_CLASS_MAPPING
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mapping = DATA_DESCRIPTOR_CLASS_MAPPING

def unified_document_loader(uri: str) -> Dict:
    """Load a document from a local file or a remote URI."""
    if uri.startswith(("http://", "https://")):
        response = requests.get(uri, headers={"accept": "application/json"}, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch remote document: {response.status_code} - {response.text}")
            return {}
    else:
        with open(uri, "r") as f:
            return json.load(f)

class Data(BaseModel):
    uri: str
    local_path: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def set_local_path(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set the local path to an absolute path if provided."""
        local_path = values.get("local_path")
        if local_path:
            values["local_path"] = os.path.abspath(local_path) + "/"
        jsonld.set_document_loader(lambda uri,options:{
            "contextUrl": None,  # No special context URL
            "documentUrl": uri,  # The document's actual URL
            "document": unified_document_loader(uri),  # The parsed JSON-LD document
        }) 
        return values

    @cached_property
    def json(self) -> Dict:
        """Fetch the original JSON data."""
        logger.info(f"Fetching JSON data from {self.uri}")
        return unified_document_loader(self.uri)

    @cached_property
    def expanded(self) -> Any:
        """Expand the JSON-LD data."""
        logger.info(f"Expanding JSON-LD data for {self.uri}")
        return jsonld.expand(self.uri, options={"base": self.uri})

    @cached_property
    def normalized(self) -> str:
        """Normalize the JSON-LD data."""
        logger.info(f"Normalizing JSON-LD data for {self.uri}")
        return jsonld.normalize(
            self.uri, options={"algorithm": "URDNA2015", "format": "application/n-quads"}
        )

    @cached_property
    def python(self) -> Optional[Any]:
        """Map the data to a Pydantic model based on URI."""
        logger.info(f"Mapping data to a Pydantic model for {self.uri}")
        model_key = self._extract_model_key(self.uri)
        if model_key and model_key in mapping:
            model = mapping[model_key]
            return model(**self.json)
        logger.warning(f"No matching model found for key: {model_key}")
        return None

    def _extract_model_key(self, uri: str) -> Optional[str]:
        """Extract a model key from the URI."""
        parts = uri.strip("/").split("/")
        if len(parts) >= 2:
            return parts[-2]
        return None

    @property
    def info(self) -> str:
        """Return a detailed summary of the data."""
        res = f"{'#' * 100}\n"
        res += f"###   {self.uri.split('/')[-1]}   ###\n"
        res += f"{'#' * 100}\n"
        res += f"URI: {self.uri}\n"
        res += f"JSON Version:\n {json.dumps(self.json, indent=2)}\n"
        res += f"Expanded Version:\n {json.dumps(self.expanded, indent=2)}\n"
        res += f"Normalized Version:\n {self.normalized}\n"
        res += f"Pydantic Model Instance:\n {self.python}\n"
        return res


if __name__ == "__main__":
    #online
    # d = Data(uri = "https://espri-mod.github.io/mip-cmor-tables/activity/cmip.json")
    # print(d.info)
    #offline
    print(Data(uri = ".cache/repos/mip-cmor-tables/activity/cmip.json").info)

