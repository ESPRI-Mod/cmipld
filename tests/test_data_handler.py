
import pytest
from unittest.mock import patch
from pydantic import ValidationError
from cmipld.core.data_handler import JsonLdResource

mock_json_data = {"@context": "http://example.com/context", "name": "Test"}

@pytest.fixture
def data_instance():
    return JsonLdResource(uri="http://example.com/resource")

@patch("cmipld.core.data_handler.unified_document_loader", return_value=mock_json_data)
def test_json(mock_loader, data_instance):
    assert data_instance.json == mock_json_data
    mock_loader.assert_called_once_with("http://example.com/resource")

def test_invalid_uri():
    with pytest.raises(ValidationError):
        JsonLdResource(uri=123)  # Invalid URI type

def test_local_path():
    data = JsonLdResource(uri="http://example.com/resource", local_path="./data")
    assert data.local_path.endswith("/data/")
