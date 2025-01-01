from dilirank import read_dilirank_data
from chembl import get_molecules_by_name
from storage import db_storer

import pandas as pd
from pathlib import Path

def collect_compounds() -> pd.DataFrame:
    """
    Collects and processes compound data by integrating information from the DILIrank dataset and
    retrieving corresponding chemical information via ChEMBL. 

    This function reads the DILIrank dataset, iterates through each compound in the dataset, and 
    retrieves matching molecule data from ChEMBL using their names. Retrieved compound data is 
    merged with the original DILIrank dataset and returned as a combined dataframe for further 
    analysis.

    :raises IOError: If DILIrank data cannot be read.
    :raises Exception: If there are issues with retrieving data from ChEMBL.
    :raises ValueError: If the merging operation fails due to mismatched or missing keys.

    :return: A DataFrame containing the original DILIrank data augmented with chemical
        information retrieved from ChEMBL for the compounds. The returned DataFrame
        has the compound name as the key to merge the datasets.
    :rtype: pd.DataFrame
    """
    dilirank_df = read_dilirank_data().head(10)


    chembl_data = []
    total = len(dilirank_df)
    pixels = 40 # Number of characters for the progress bar
    for idx, compound in enumerate(dilirank_df.itertuples()):
        pct = (idx+1) / total
        done =int(pct*pixels)
        compound_name = compound._2
        chembl_compounds = get_molecules_by_name(compound_name, clean=True, compact=True)

        print("\r", end="") # Reset to the start of the line (re-use same line for progress)
        # Color of progress bar: Yellow in 1st third, blue in 2nd third, and green in final third.
        color = "\033[33m" if pct < 0.33 else ("\033[34m" if pct < 0.66 else "\033[32m")
        fmt_string = "{:>4}/{:>4}[" + color + "{:<" + str(pixels) + "}\033[0m] {}: {}"
        print(fmt_string.format(idx+1, total, "*" * done, compound_name, len(chembl_compounds)), end="", flush=True)

        for chembl_compound in chembl_compounds:
            print(".", end="", flush=True)
            chembl_data.append({
                "Compound Name": compound_name,
                **chembl_compound
            })
    return pd.merge(dilirank_df, pd.DataFrame(chembl_data), on='Compound Name', how='left')


def save_compounds(df: pd.DataFrame, data_directory: str='./data', data_file: str='diliranked_compounds'):
    """
    Stores a DataFrame containing compound data into a CSV file. If the output directory
    does not exist, it creates the necessary subdirectory structure before storing the file.

    :param df: A pandas DataFrame containing compound data to be saved.
    :type df: pandas.DataFrame
    :param data_directory: The directory where the CSV file will be stored.
    :type data_directory: str
    :default data_directory: ./data (relative to the current working directory)
    :param data_file: The name of the file where the DataFrame will be saved (the .csv extension is added automatically).
    :type data_file: str
    :default data_file: 'diliranked_compounds.csv'
    
    :return: None
    """
    store_path = Path(data_directory, 'chembl')
    if not store_path.exists():
        store_path.mkdir()
    df.to_csv(Path(store_path, data_file + ".csv"), index=False)


def collect_activities(compounds: list[str]) -> pd.DataFrame:
    pass

if __name__ == "__main__":
    compound_df = collect_compounds()
    # save_compounds(compound_df)
    # store_compounds(compound_df)
    db_storer.store_compounds(compound_df)
    print("Done")