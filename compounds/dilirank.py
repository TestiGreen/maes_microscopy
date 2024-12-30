DEFAULT_DATA_DIRECTORY = r'./data/dilirank'
DEFAULT_DATA_FILE = 'DILIrank-DILIscore_List.xlsx'

import pandas as pd
from pathlib import Path

def read_dilirank_data(data_directory: str=DEFAULT_DATA_DIRECTORY, data_file: str=DEFAULT_DATA_FILE) -> pd.DataFrame:
    data_file_path = Path(data_directory + '/' + data_file).absolute()
    df = pd.read_excel(data_file_path, sheet_name='DILIrank', header=1)
    return df