import requests

CHEMBL_BASE_URL = "https://www.ebi.ac.uk/chembl/api"
CHEMBL_MOLECULE_SEARCH = "data/molecule/search?q={}"

def get_molecules_by_name(name):
    url = CHEMBL_BASE_URL + "/" + CHEMBL_MOLECULE_SEARCH.format(name)
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)

    if not response.ok:
        raise Exception("Error fetching molecules by name: {}".format(response.text))

    response_map = response.json()
    molecules = response_map["molecules"]
    return molecules