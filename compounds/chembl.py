from typing import Any, Callable

import requests

CHEMBL_BASE_URL = "https://www.ebi.ac.uk/chembl/api"
CHEMBL_MOLECULE_SEARCH = "data/molecule/search?q={}" # molecule pref name
CHEMBL_ACTIVITY_SEARCH = "data/activity/search?q={}" # chembl_id

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

    :param name: (str) The name of the molecule to search for.
    :type name: str
    :param filter_noname: If True, removes molecules without a name (`pref_name` field).
    :type filter_noname: bool
    :default filter_noname: False
    :param filter_nosmile: If True, removes molecules without a SMILES string (`molecule_structures.canonical_smiles` field).
    :type filter_nosmile: bool
    :default filter_nosmile: False
    :param filter_noinchi: If True, removes molecules without an InChI string (`molecule_structures.standard_inchi` field).
    :type filter_noinchi: bool
    :default filter_noinchi: False
    :param filter_noinchikey: If True, removes molecules without an InChIKey string (`molecule_structures.standard_inchi_key` field).
    :type filter_noinchikey: bool
    :default filter_noinchikey: False
    :param clean: If True, applies all trimming filters (noname, nosmile, noinchi, noinchikey).
    :type clean: bool
    :default clean: False
    :param compact: (bool, optional) If True, returns a compact notation of the molecules as output, otherwise returns the full JSON representation.
    :type compact: bool
    default compact: False

    :return: Returns a list of molecules if `compact` is False, otherwise returns a
            compact representation in the form of a dictionary.
    :rtype: list[dict[str, Any]] or dict[str, Any]

    :raise: If the request to fetch molecules fails, an exception is raised containing
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

def get_chemical_activity(chembl_id) -> list[dict[str, Any]]:
    url = CHEMBL_BASE_URL + "/" + CHEMBL_ACTIVITY_SEARCH.format(chembl_id)

    current_offset = 0
    current_limit = 20
    paging_query = '&offset={}&limit={}'.format

    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)

    if not response.ok:
        raise Exception("Error fetching activities for {}: {}".format(chembl_id, response.text))

    response_map = response.json()
    return response_map["activities"]


class MoleculeFilterer:
    """
    A class for filtering and processing a list of molecular data.

    This class is designed to handle a collection of molecules represented as
    dictionaries and provides methods to filter out invalid or incomplete molecular
    entries based on specific criteria such as the presence of a name, SMILES,
    InChI, or InChI key. It also facilitates retrieving the processed molecular data
    and generating a condensed representation of key properties in the molecules.
    """
    def __init__(self, molecules: list[dict[str, Any]]):
        """
        Represents a container for storing molecular data. The class provides
        functionality to initialize and maintain a collection of molecule
        information in a structured way.

        :param molecules: A list containing dictionary representations of molecules.
         Each dictionary represents a molecule with its associated properties
         and data.  The structure of the dictionary should be the same as what comes
         from the CHEMBL API.
         :type molecules: list[dict[str, Any]]
        """
        self.__molecules = molecules

    def trim_without_name(self):
        """
        Filters out molecules that do not have a preferred name (pref_name property) and updates the instance's
        molecule list accordingly.

        :return: The current instance with molecules that have a preferred name.
        :rtype: MoleculeFilterer
        """
        self.__molecules = filter(lambda m: m["pref_name"] is not None, self.__molecules)
        return self

    def trim_without_smiles(self):
        """
        Filters out molecules that do not have valid molecule structures or canonical SMILES strings
        from the internal dataset. This function ensures that only molecules with complete
        and valid structural information are retained in the collection.

        :return: Returns the instance of the class with filtered molecule data.
        :rtype: MoleculeFilterer
        """
        self.__molecules = filter(lambda m: m["molecule_structures"] is not None and
                                            m["molecule_structures"]["canonical_smiles"] is not None, self.__molecules)
        return self

    def trim_without_inchi(self):
        """
        Filters out molecules that do not have a valid standard InChI.  Molecules without the "molecule_structures"
        definition will also be removed.

        :return: Returns the current instance of the class after filtering the
            molecules.
        :rtype: MoleculeFilterer
        """
        self.__molecules = filter(lambda m: m["molecule_structures"] is not None and
                                            m["molecule_structures"]["standard_inchi"] is not None, self.__molecules)
        return self

    def trim_without_inchi_key(self):
        """
        Filters out molecules from the current molecule collection that do not contain
        a valid "molecule_structures" entry or a "standard_inchi_key" key.

        :return: Returns the current object instance with filtered molecules.
        rtype: MoleculeFilterer
        """
        self.__molecules = filter(lambda m: m["molecule_structures"] is not None and
                                            m["molecule_structures"]["standard_inchi_key"] is not None, self.__molecules)
        return self

    def clean(self):
        """
        Cleans the dataset by applying each of `trim...` operations.

        :return: The cleaned dataset with all invalid entries removed.
        :rtype: MoleculeFilterer
        """
        return self.trim_without_name().trim_without_smiles().trim_without_inchi().trim_without_inchi_key()

    def trim_on_predicate(self, predicate: Callable[[dict[str, Any]], bool]):
        """
        Filters the internal list of dictionaries based on a given predicate function.
        This method iterates through the list and keeps only those entries for which
        the predicate function returns `True`.

        :param predicate: A callable that takes a dictionary and returns a boolean value.
                          Determines whether an entry should be included in the final list.
        :return: The current object instance with filtered molecules.
        :rtype: MoleculeFilterer
        """
        self.__molecules = filter(predicate, self.__molecules)
        return self

    def get_molecules(self) -> list[dict[str, Any]]:
        """
        Retrieves the list of stored molecule data in their current state.

        This method provides access to the internally stored molecules in the form
        of a list of dictionaries. Each dictionary contains information representing
        a molecule in the format returned by the CHEMBL API.  This is a snapshot of the
        list - further filtering of the list after calling this method will not be
        reflected in the returned list, and filterning the returned list will not change
        the values stored internally in this class.

        :return: A list of dictionaries, where each dictionary represents a molecule.
        :rtype: list[dict[str, Any]]
        """
        return list(self.__molecules)

    def get_compressed_notation(self) -> list[dict[str, Any]]:
        """
        Generates a compressed representation of molecule-related data.

        The function processes the internal list of molecule records available in the
        attribute. It extracts a subset of details about each molecule, including key identifiers,
        names, properties, classifications, and structural information. For molecule structures,
        the function provides SMILES, InChI, and InChIKey if the structure data is present. It also
        handles optional data such as synonyms and classifications.

        :return: A list of dictionaries representing molecules, each containing a compressed representation of
                 the molecule's key data.
        :rtype: list[dict[str, Any]]
        """
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