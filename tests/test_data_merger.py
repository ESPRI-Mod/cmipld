from pathlib import Path
import unittest
from pydantic import Json
import pytest
from unittest.mock import patch, MagicMock
from typing import Set
from cmipld.core.data_handler import JsonLdResource
from cmipld.core.service.data_merger import DataMerger

def test_remote_organisation_ipsl():
    
    uri = "https://espri-mod.github.io/mip-cmor-tables/organisation/ipsl.json"
    merger = DataMerger(data= JsonLdResource(uri = uri), allowed_base_uris={"https://espri-mod.github.io/mip-cmor-tables/"})
    jsonlist = merger.merge_linked_json()
    print(jsonlist)

    assert jsonlist[-1]["established"]==1991

def test_remote_from_project_ipsl():

    uri =  "https://espri-mod.github.io/CMIP6Plus_CVs/institution_id/ipsl.json"
    merger = DataMerger(data= JsonLdResource(uri = uri), allowed_base_uris={"https://espri-mod.github.io/mip-cmor-tables/"})
    jsonlist = merger.merge_linked_json()
    print(jsonlist)


    assert jsonlist[-1]["established"]==1998 # this is a overcharged value 'from 1991 in ipsl definition in the universe to 1996 in ipsl in cmip6plus_cvs 
    assert jsonlist[-1]["myprop"]=="42" # a new property definition in the project cv


def test_local_organisation_ipsl():
    
    uri = ".cache/repos/mip-cmor-tables/organisation/ipsl.json"
    merger = DataMerger(data= JsonLdResource(uri = uri), allowed_base_uris={"https://espri-mod.github.io/mip-cmor-tables/"})
    jsonlist = merger.merge_linked_json()
    print(jsonlist)

    assert jsonlist[-1]["established"]==1991

def test_local_from_project_ipsl():

    uri =  ".cache/repos/CMIP6Plus_CVs/institution_id/ipsl.json"
    merger = DataMerger(data= JsonLdResource(uri = uri), allowed_base_uris={"https://espri-mod.github.io/mip-cmor-tables/"})
    jsonlist = merger.merge_linked_json()
    print(jsonlist)


    assert jsonlist[-1]["established"]==1998 # this is a overcharged value 'from 1991 in ipsl definition in the universe to 1996 in ipsl in cmip6plus_cvs 
    assert jsonlist[-1]["myprop"]=="42" # a new property definition in the project cv


def test_local_project_all():
    repos_dir = Path(".cache/repos/CMIP6Plus_CVs") 
    for dir in repos_dir.iterdir():
        
        if dir.is_dir() and dir /"000_context.jsonld" in list(dir.iterdir()):
            for term_uri in dir.iterdir():
                if "000_context" not in term_uri.stem:
                    term = JsonLdResource(uri=str(term_uri))
                    mdm = DataMerger(data= term, allowed_base_uris={"https://espri-mod.github.io/mip-cmor-tables/"})
                    
                    print(mdm.merge_linked_json()[-1])
            
    assert 1==2
    


# def test_real_remote_merger():
#     uri = "https://espri-mod.github.io/mip-cmor-tables/institution/ipsl.json"
#

#TODO UNIT TEST


#
# @patch("cmipld.core.data_handler.JsonLdResource")
# @patch('cmipld.core.service.data_merger.DataMerger._get_next_id')
# def test_single_customization_mehhtprge(mock_resource,mock_next_id, setup_data):
#     """Test merging with a single customization."""
#     original_ressource, custom_ressource_1, _, allowed_base_uris = setup_data
#
#     mock_resource.side_effect = lambda uri: MagicMock(
#         json=custom_ressource_1.json if uri.endswith("custom1.json") else original_ressource.json,
#         expanded=custom_ressource_1.expanded if uri.endswith("custom1.json") else original_ressource.expanded,
#         uri=uri
#     )
#     merger = DataMerger(data=mock_resource(custom_ressource_1.uri) , allowed_base_uris=allowed_base_uris)
#     print(merger.data)
#     with patch.object(DataMerger, '_get_next_id', return_value="http://example.org/original.json") as mock_get_next_id:
#         mock_next_instance_data = mock_resource.return_value
#         mock_next_instance_data = mock_resource(original_ressource.uri)
#         merged_data = merger.merge_linked_json()
#         print(merged_data)
#
#         assert len(merged_data) == 2
#         assert merged_data[1]["name"] == "Custom 1"
#         assert "new_field" in merged_data[1]
#
# @patch("cmipld.core.data_handler.JsonLdResource")
# def test_multiple_customizations_merge(mock_resource, setup_data):
#     """Test merging with multiple customizations."""
#     _, custom_ressource_1, custom_ressource_2, allowed_base_uris = setup_data
#
#     mock_resource.side_effect = lambda uri: MagicMock(
#         json=custom_ressource_2 if uri.endswith("custom2.json") else custom_ressource_1,
#         expanded=[custom_ressource_2 if uri.endswith("custom2.json") else custom_ressource_1],
#         uri=uri
#     )
#
#     merger = DataMerger(data=mock_resource("http://example.org/custom1"), allowed_base_uris=allowed_base_uris)
#     merged_data = merger.merge_linked_json()
#
#     assert len(merged_data) == 2
#     assert merged_data[1]["description"] == "Custom description 2"
#     assert "additional_field" in merged_data[1]
#
# @patch("cmipld.core.data_handler.JsonLdResource")
# def test_cycle_prevention(mock_resource, setup_data):
#     """Test that cycles are prevented in recursive merges."""
#     original_ressource, _, _, allowed_base_uris = setup_data
#
#     mock_resource.side_effect = lambda uri: MagicMock(
#         json=original_ressource if uri.endswith("original.json") else original_json,
#         expanded=[original_ressource if uri.endswith("original.json") else original_json],
#         uri=uri
#     )
#
#     merger = DataMerger(data=mock_resource("http://example.org/original"), allowed_base_uris=allowed_base_uris)
#     merged_data = merger.merge_linked_json()
#
#     # Cycle detection should result in only one merged result (original).
#     assert len(merged_data) == 1
#     assert merged_data[0]["name"] == "Original"
#
