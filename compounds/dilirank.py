DEFAULT_DATA_DIRECTORY = r'./data/dilirank'
DEFAULT_DATA_FILE = 'DILIrank-DILIscore_List.xlsx'

import pandas as pd
from pathlib import Path

def read_dilirank_data(data_directory: str=DEFAULT_DATA_DIRECTORY, data_file: str=DEFAULT_DATA_FILE) -> pd.DataFrame:
    """
    Reads the DILIrank data from the specified Excel file and sheet. This function returns
    a DataFrame containing the retrieved data.

    :param data_directory: The directory where the DILIrank data file is located.
    :type data_directory: str
    :default data_directory: Specified by the DEFAULT_DATA_DIRECTORY constant.
    :param data_file: The name of the DILIrank data file to be read.
    :type data_file: str
    :default data_file: Specified by the DEFAULT_DATA_FILE constant.

    :return: A pandas DataFrame containing the DILIrank data.
    :rtype: pd.DataFrame
    """
    data_file_path = Path(data_directory + '/' + data_file).absolute()
    df = pd.read_excel(data_file_path, sheet_name='DILIrank', header=1)
    return df