from typing import Any

import requests

CHEMBL_BASE_URL = "https://www.ebi.ac.uk/chembl/api"
CHEMBL_MOLECULE_SEARCH = "data/molecule/search?q={}"

def get_molecules_by_name(name,
                          filter_noname=False,
                          filter_nosmile=False,
                          filter_noinchi=False,
                          filter_noinchikey=False,
                          clean=False,
                          compact=False) -> list[dict[str, Any]]:
    """
    Fetch molecules from the ChemBL database by their name and apply optional filtering and formatting options.

    This function queries the CHEMBL database to retrieve molecules based on a given name.  Results can be filtered
    to remove those that don't have names, smiles, standard inchis, or standard inchi keys.  The resulting molecules
    can be returned in their normal format as retrieved from the database or in a compact format:
    
    <code>
    {
        "chembl_id": "CHEMBL1234",
        "name": "Murine serum albumin",
        "indication_class": "Inhibitor",
        "inorganic_flag": False,
        "max_phase": "4.0",
        "properties": { ... as returned by the CHEMBL API ... },
        "smiles": "CC(C)C(=O)O",
        "inchi": "InChI=1S/C6H12O6/c7-6-4-2-1-3-5-6/h1-5H",
        "inchi_key": "NKGPJODWTZCHGF-KQYNXXCUSA-N",
        "synonyms": ["synonym1", "synonym2"],
        "atc_classifications": ["A01AA01", "A01AA02"],
        "type": "MOL",
        "natural": 1,
        "topical": False,
        "oral": False,
        "parenteral": False,
    }
    </code>

    Parameters:
        name (str): The name of the molecule to search for.
        filter_noname (bool, optional): If True, removes molecules without a name (`pref_name` field).
        filter_nosmile (bool, optional): If True, removes molecules without a SMILES string (`molecule_structures.canonical_smiles` field).
        filter_noinchi (bool, optional): If True, removes molecules without an InChI string (`molecule_structures.standard_inchi` field).
        filter_noinchikey (bool, optional): If True, removes molecules without an InChIKey string (`molecule_structures.standard_inchi_key` field).
        clean (bool, optional): If True, applies all trimming filters (noname, nosmile, noinchi, noinchikey).
        compact (bool, optional): If True, returns a compact notation of the molecules as output, otherwise returns the full JSON representation.

    Returns:
        list: Returns a list of molecules if `compact` is False, otherwise returns a
        compact representation in the form of a dictionary.

    Raises:
        Exception: If the request to fetch molecules fails, an exception is raised containing
        the error message from the response.
    """
    url = CHEMBL_BASE_URL + "/" + CHEMBL_MOLECULE_SEARCH.format(name)
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)

    if not response.ok:
        raise Exception("Error fetching molecules by name: {}".format(response.text))

    response_map = response.json()
    molecules = response_map["molecules"]
    filterer = MoleculeFilterer(molecules)
    if filter_noname or clean:
        filterer.trim_without_name()
    if filter_nosmile or clean:
        filterer.trim_without_smiles()
    if filter_noinchi or clean:
        filterer.trim_without_inchi()
    if filter_noinchikey or clean:
        filterer.trim_without_inchi_key()

    if compact:
        return filterer.get_compressed_notation()
    else:
        return filterer.get_molecules()

class MoleculeFilterer:
    def __init__(self, molecules: list[dict[str, Any]]):
        self.__molecules = molecules

    def trim_without_name(self):
        self.__molecules = filter(lambda m: m["pref_name"] is not None, self.__molecules)
        return self

    def trim_without_smiles(self):
        self.__molecules = filter(lambda m: m["molecule_structures"] is not None and
                                            m["molecule_structures"]["canonical_smiles"] is not None, self.__molecules)
        return self

    def trim_without_inchi(self):
        self.__molecules = filter(lambda m: m["molecule_structures"] is not None and
                                            m["molecule_structures"]["standard_inchi"] is not None, self.__molecules)
        return self

    def trim_without_inchi_key(self):
        self.__molecules = filter(lambda m: m["molecule_structures"] is not None and
                                            m["molecule_structures"]["standard_inchi_key"] is not None, self.__molecules)
        return self

    def clean(self):
        return self.trim_without_name().trim_without_smiles().trim_without_inchi().trim_without_inchi_key()

    def get_molecules(self) -> list[dict[str, Any]]:
        return list(self.__molecules)

    def get_compressed_notation(self) -> list[dict[str, Any]]:
        return [
            {
                "chembl_id": m["molecule_chembl_id"],
                "name": m["pref_name"],
                "indication_class": m["indication_class"],
                "inorganic_flag": m["inorganic_flag"],
                "max_phase": m["max_phase"],
                "properties": m["molecule_properties"],
                "smiles": m["molecule_structures"]["canonical_smiles"] if m["molecule_structures"] is not None else None,
                "inchi": m["molecule_structures"]["standard_inchi"] if m["molecule_structures"] is not None else None,
                "inchi_key": m["molecule_structures"]["standard_inchi_key"] if m["molecule_structures"] is not None else None,
                "synonyms": [s["molecule_synonym"] for s in m["molecule_synonyms"]] if m["molecule_synonyms"] is not None else [],
                "atc_classifications": m["atc_classifications"],
                "type": m["molecule_type"],
                "natural": m["natural_product"],
                "topical": m["topical"],
                "oral": m["oral"],
                "parenteral": m["parenteral"],
            }
            for m in self.__molecules
        ]