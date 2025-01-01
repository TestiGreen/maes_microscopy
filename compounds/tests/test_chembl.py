import json
from unittest.mock import patch, Mock

import pytest
from compounds.chembl import get_molecules_by_name, get_chemical_activity


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


@patch("compounds.chembl.requests.get")
def test_get_chemical_activity_with_valid_chembl_id(mock_get):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "activities": [{"activity_id": "1", "standard_value": "10"}],
        "page_meta": {"next": None}
    }
    mock_get.return_value = mock_response

    chembl_id = "CHEMBL12345"
    result = get_chemical_activity(chembl_id)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["activity_id"] == "1"
    assert result[0]["standard_value"] == "10"


@patch("compounds.chembl.requests.get")
def test_get_chemical_activity_with_multiple_pages(mock_get):
    mock_response_page1 = Mock()
    mock_response_page1.ok = True
    mock_response_page1.json.return_value = {
        "activities": [{"activity_id": "1", "standard_value": "10"}],
        "page_meta": {"next": "next"}
    }

    mock_response_page2 = Mock()
    mock_response_page2.ok = True
    mock_response_page2.json.return_value = {
        "activities": [{"activity_id": "2", "standard_value": "20"}],
        "page_meta": {"next": None}
    }

    mock_get.side_effect = [mock_response_page1, mock_response_page2]

    chembl_id = "CHEMBL12345"
    result = get_chemical_activity(chembl_id)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["activity_id"] == "1"
    assert result[1]["activity_id"] == "2"


@patch("compounds.chembl.requests.get")
def test_get_chemical_activity_with_multiple_pages_and_failure(mock_get):
    mock_response_page1 = Mock()
    mock_response_page1.ok = True
    mock_response_page1.json.return_value = {
        "activities": [{"activity_id": "1", "standard_value": "10"}],
        "page_meta": {"next": "next"}
    }

    mock_response_page2 = Mock()
    mock_response_page2.ok = True
    mock_response_page2.json.return_value = {
        "activities": [{"activity_id": "2", "standard_value": "20"}],
        "page_meta": {"next": "next"}
    }

    mock_response_page3 = Mock()
    mock_response_page3.ok = False
    mock_response_page3.text = "Invalid request"

    mock_get.side_effect = [mock_response_page1, mock_response_page2, mock_response_page3]

    chembl_id = "CHEMBL12345"
    result = get_chemical_activity(chembl_id)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["activity_id"] == "1"
    assert result[1]["activity_id"] == "2"


@patch("compounds.chembl.requests.get")
def test_get_chemical_activity_with_invalid_chembl_id(mock_get):
    mock_response = Mock()
    mock_response.ok = False
    mock_response.text = "Invalid request"
    mock_get.return_value = mock_response

    chembl_id = "INVALID_CHEMBL"
    result = get_chemical_activity(chembl_id)

    assert isinstance(result, list)
    assert len(result) == 0


@patch("compounds.chembl.requests.get")
def test_get_chemical_activity_with_empty_response(mock_get):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "activities": [],
        "page_meta": {"next": None}
    }
    mock_get.return_value = mock_response

    chembl_id = "CHEMBL_EMPTY"
    result = get_chemical_activity(chembl_id)

    assert isinstance(result, list)
    assert len(result) == 0


def test_get_activity_by_chemblid_integration():
    activities = get_chemical_activity("CHEMBL1647")
    assert isinstance(activities, list)
    assert len(activities) > 0
    assert activities[0]["molecule_chembl_id"] == "CHEMBL1647"
    assert activities[0]["activity_id"] == 2357368

