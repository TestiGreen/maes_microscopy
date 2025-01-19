import sys

from dilirank import read_dilirank_data
from chembl import get_molecules_by_name, get_chemical_activity
from storage import db_storer

import pandas as pd
from pathlib import Path

# When DEBUG_MODE is True, few, randomly sampled compounds will be processed, and fewer activities per
# compound will be processed to make test routines faster.
DEBUG_MODE = False


def __update_progress(idx, total, txt_1, txt_2):
    """
    Updates and displays a progress bar in the terminal with a specific color based on the
    completion percentage. The progress bar showcases the current progress towards the total
    goal, while also displaying descriptive texts to provide more information about the
    current state.

    :param idx: Current progress value, representing the current count or step of the progress.
    :type idx: int
    :param total: The total value or steps to reach 100% completion of the progress bar.
    :type total: int
    :param txt_1: A string to be presented after the progress bar, providing additional context.
    :type txt_1: str
    :param txt_2: Another string displayed at the end of the progress bar, offering further
        details or clarification.
    :type txt_2: str
    :return: None
    """
    pixels = 40
    pct = idx / total
    done = int(pct * pixels)

    print("\r", end="")  # Reset to the start of the line (re-use same line for progress)
    # Color of progress bar: Yellow in 1st third, blue in 2nd third, and green in final third.
    color = "\033[33m" if pct < 0.33 else ("\033[34m" if pct < 0.66 else "\033[32m")
    fmt_string = "{:>4}/{:>4}[" + color + "{:<" + str(pixels) + "}\033[0m] {}: {}"
    print(fmt_string.format(idx, total, "*" * done, txt_1, txt_2), end="", flush=True)


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
    dilirank_df = read_dilirank_data()

    if DEBUG_MODE:
        dilirank_df = dilirank_df.sample(n=10)

    total = len(dilirank_df)
    for idx, compound in enumerate(dilirank_df.itertuples()):
        chembl_data = []
        compound_name = compound._2
        chembl_compounds = get_molecules_by_name(compound_name, clean=True, compact=True)

        __update_progress(idx+1, total, compound_name, '')

        for chembl_compound in chembl_compounds:
            # print(".", end="", flush=True)
            chembl_data.append({
                "Compound Name": compound_name,
                **chembl_compound
            })

        # Store the just-read compounds into a table
        if len(chembl_data) > 0:
            chembl_df = pd.DataFrame(chembl_data)
            cmpd_df = pd.merge(dilirank_df, chembl_df, on='Compound Name', how='inner')
            db_storer.store_compounds(cmpd_df, new_db=(idx == 0))

    print("")
    # return pd.merge(dilirank_df, pd.DataFrame(chembl_data), on='Compound Name', how='left')
    return db_storer.read_compounds()


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


def collect_activities(compounds_df: pd.DataFrame) -> pd.DataFrame:
    """
    Collects activities associated with the provided compounds.

    This function processes a DataFrame of compounds, retrieves their unique
    compound IDs, and gathers their respective activity data. It also tracks
    the progress of data collection and updates the progress accordingly.
    The retrieved activity information is aggregated into a new DataFrame,
    which is then returned to the caller.

    :param compounds_df: A DataFrame containing compound data, where each
        compound is expected to have a 'chembl_id' column.
    :type compounds_df: pd.DataFrame
    :return: A DataFrame containing chemical activity data for the compounds
        provided in the input. Each row in the DataFrame corresponds to an
        activity record, and each has a column named CHEMBL_ID for the compound it applies to.
    :rtype: pd.DataFrame
    """
    compound_ids = compounds_df['chembl_id'].unique().tolist()

    activities = []
    total = len(compound_ids)
    for idx, compound_id in enumerate(compound_ids):
        __update_progress(idx, total, compound_id, "")

        cmpd_activities = [{"chembl_id": compound_id, **activity}
                           for activity in get_chemical_activity(compound_id, 50 if DEBUG_MODE else sys.maxsize)]
        activities.extend(cmpd_activities)

        __update_progress(idx+1, total, compound_id, str(len(cmpd_activities)))

    activity_df = pd.DataFrame(activities)
    print("")
    return activity_df

if __name__ == "__main__":
    compound_df = collect_compounds()
    db_storer.store_compounds(compound_df)
    db_storer.store_activities(collect_activities(compound_df), new_db=True)
    print("Done")