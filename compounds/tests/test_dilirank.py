from pathlib import Path

import pandas as pd
import pytest
from compounds.dilirank import read_dilirank_data


@pytest.fixture
def mock_data_file(tmp_path):
    data_directory = tmp_path
    data_file = "test_data.xlsx"
    file_path = data_directory / data_file
    df = pd.DataFrame({
        "Compound Name": ["Compound1", "Compound2"],
        "Category": ["Most-DILI-Concern", "Less-DILI-Concern"],
    })
    df.to_excel(file_path, sheet_name='DILIrank', index=False, header=True, startrow=1)
    return str(data_directory), data_file


def test_read_dilirank_data_with_valid_file(mock_data_file):
    data_directory, data_file = mock_data_file
    df = read_dilirank_data(data_directory=data_directory, data_file=data_file)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["Compound Name", "Category"]


def test_read_dilirank_data_with_nonexistent_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_dilirank_data(data_directory=str(tmp_path), data_file="nonexistent_file.xlsx")


def test_read_dilirank_data_with_invalid_format_file(tmp_path):
    data_directory = tmp_path
    data_file = "invalid_format.txt"
    file_path = data_directory / data_file
    file_path.write_text("This is a test file with invalid format.")
    with pytest.raises(ValueError):
        read_dilirank_data(data_directory=str(data_directory), data_file=data_file)

def test_read_dilirank():
    df = read_dilirank_data(data_directory='../../data/dilirank')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["LTKBID", "Compound Name", "Severity Class", "Label Section", "vDILIConcern", "Version"]
