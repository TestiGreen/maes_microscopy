from dilirank import read_dilirank_data
from chembl import get_molecules_by_name

import pandas as pd
from pathlib import Path

def collect_compounds() -> pd.DataFrame:
    dilirank_df = read_dilirank_data()


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


def store_compounds(df: pd.DataFrame):
    store_path = Path('.', 'data', 'chembl')
    if not store_path.exists():
        store_path.mkdir()
    df.to_csv(Path(store_path, 'diliranked_compounds.csv'), index=False)

if __name__ == "__main__":
    compound_df = collect_compounds()
    store_compounds(compound_df)
    print("Done")