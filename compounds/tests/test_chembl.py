import json
from unittest.mock import patch, Mock

import pytest
from compounds.chembl import get_molecules_by_name


@pytest.fixture
def mock_response_ok():
    mock_response = Mock()
    mock_response.ok = True

    with open('mercaptopurine.json', 'r') as resp_example:
        mock_response.json.return_value = json.load(resp_example)
    return mock_response


@pytest.fixture
def mock_response_error():
    mock_response = Mock()
    mock_response.ok = False
    mock_response.text = "Not Found"
    return mock_response


@patch("compounds.chembl.requests.get")
def test_get_molecules_by_name_with_valid_name(mock_get, mock_response_ok):
    mock_get.return_value = mock_response_ok
    result = get_molecules_by_name("mercaptopurine")
    assert isinstance(result, list)
    assert len(result) == 16
    assert result[0]["molecule_chembl_id"] == "CHEMBL1425"
    assert result[0]["pref_name"] == "MERCAPTOPURINE ANHYDROUS"


@patch("compounds.chembl.requests.get")
def test_get_molecules_by_name_with_valid_name_clean(mock_get, mock_response_ok):
    mock_get.return_value = mock_response_ok
    result = get_molecules_by_name("mercaptopurine", clean=True)
    assert isinstance(result, list)
    assert len(result) == 5


@patch("compounds.chembl.requests.get")
def test_get_molecules_by_name_with_valid_name_compact(mock_get, mock_response_ok):
    mock_get.return_value = mock_response_ok
    result = get_molecules_by_name("mercaptopurine", compact=True)
    assert isinstance(result, list)
    assert len(result) == 16
    assert result[0]["chembl_id"] == "CHEMBL1425"
    assert result[0]["name"] == "MERCAPTOPURINE ANHYDROUS"
    assert result[0]["smiles"] is not None


@patch("compounds.chembl.requests.get")
def test_get_molecules_by_name_with_invalid_name(mock_get, mock_response_error):
    mock_get.return_value = mock_response_error
    with pytest.raises(Exception) as exc_info:
        get_molecules_by_name("unknown")
    assert "Error fetching molecules by name" in str(exc_info.value)


@patch("compounds.chembl.requests.get")
def test_get_molecules_by_name_api_call(mock_get, mock_response_ok):
    mock_get.return_value = mock_response_ok
    get_molecules_by_name("mercaptopurine")
    mock_get.assert_called_once()
    assert "mercaptopurine" in mock_get.call_args[0][0]


def test_get_molecules_by_name_integration():
    molecules = get_molecules_by_name("mercaptopurine")
    assert isinstance(molecules, list)
    assert len(molecules) > 0
    assert molecules[0]["molecule_chembl_id"] == "CHEMBL1425"
    assert molecules[0]["pref_name"] == "MERCAPTOPURINE ANHYDROUS"
