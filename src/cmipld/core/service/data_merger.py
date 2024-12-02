
from typing import Dict, List, Set
from cmipld.core.data_handler import JsonLdResource
import pyld
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_dicts(original: list, custom: list) -> dict:
    """Shallow merge: Overwrites original data with custom data."""
    b = original[0]
    a = custom[0]    
    merged = {**{k: v for k, v in a.items() if k != "@id"}, **{k: v for k, v in b.items() if k != "@id"}}
    return merged

class DataMerger:
    def __init__(self, data: JsonLdResource, allowed_base_uris: Set[str]):
        self.data = data
        self.allowed_base_uris = allowed_base_uris

    def _should_resolve(self, uri: str) -> bool:
        """Check if a given URI should be resolved based on allowed URIs."""
        return any(uri.startswith(base) for base in self.allowed_base_uris)

    def _get_next_id(self, data: dict) -> str | None:
        """Extract the next @id from the data if it is a valid customization reference."""
        if isinstance(data,list):
            data = data[0]
        if "@id" in data and self._should_resolve(data["@id"]):
            return data["@id"] + ".json" 
        return None

    def merge_linked_json(self) -> List[Dict]:
        """Fetch and merge data recursively, returning a list of progressively merged Data json instances."""
        result_list = [self.data.json]  # Start with the original json object
        visited = set(self.data.uri)  # Track visited URIs to prevent cycles

        current_data = self.data
        print(current_data.expanded)

        while True:
            next_id = self._get_next_id(current_data.expanded[0])
            if not next_id or next_id in visited or not self._should_resolve(next_id):
                break
            visited.add(next_id)

            # Fetch and merge the next customization
            next_data_instance = JsonLdResource(uri=next_id)
            merged_json_data = merge_dicts([current_data.json], [next_data_instance.json])
            next_data_instance.json = merged_json_data

            # Add the merged instance to the result list
            result_list.append(merged_json_data)
            current_data = next_data_instance

        return result_list

if __name__ == "__main__":
    import warnings
    from pprint import pprint
    warnings.simplefilter("ignore")

    # test from institution_id ipsl exapnd and merge with institution ipsl
    proj_ipsl = JsonLdResource(uri = "https://espri-mod.github.io/CMIP6Plus_CVs/institution_id/ipsl.json")
    allowed_uris = {"https://espri-mod.github.io/CMIP6Plus_CVs/","https://espri-mod.github.io/mip-cmor-tables/"}
    mdm = DataMerger(data =proj_ipsl, allowed_base_uris = allowed_uris)
    #res = mdm.expand_and_merge()
    
    # print()
    # print("IN FINE")
    # 
    # [pprint(dat.expanded) for dat in res]
    #
    # print("Context ? ")
    # [pprint(dat.context) for dat in res]
    #
    # print("JUST DO IT : ")
    # 
    # compact = pyld.jsonld.compact(res[-1].expanded,res[-1].context)
    # compact.pop("@context")
    # pprint(compact)
    #
    # print()
    # print()
    # print("OR....")
    # print()
    
    json_list = mdm.merge_linked_json()

    pprint([res for res in json_list])



    #### ARCHIVE 
    # return the list of Data instances

    # def expand_and_merge(self) -> List[Data]:
    #     """Fetch and merge data recursively, returning a list of progressively merged Data instances."""
    #     result_list = [self.data]  # Start with the original data object
    #     visited = set(self.data.uri)  # Track visited URIs to prevent cycles
    #     current_data = self.data
    #
    #     while True:
    #
    #         next_id = self._get_next_id(current_data.expanded[0])
    #         if not next_id or next_id in visited or not self._should_resolve(next_id):
    #             break
    #         visited.add(next_id)
    #
    #         # Fetch and merge the next customization
    #         next_data_instance = Data(uri=next_id)
    #
    #         merged_data = [merge_dicts(current_data.expanded, next_data_instance.expanded)]
    #         merged_data[0]["@id"] = next_data_instance.expanded[0]["@id"]
    #
    #         # Create a new Data instance with the merged result
    #         next_data_instance.expanded = merged_data
    #
    #         # Add the merged instance to the result list
    #         result_list.append(next_data_instance)
    #
    #         # Update current_data to the latest merged result for the next iteration
    #         current_data = next_data_instance
    #
    #     return result_list

