import pandas as pd
import numpy as np
import pandas as pd
import pytest
import tifffile as tiff  # Added for saving TIFF files
from broad_babel.query import run_query
import os

from jump_portrait.fetch import get_item_location_info, get_jump_image_batch, get_negative_ctrl_location_for_plate
from jump_portrait.s3 import get_image_from_s3uri

from jump_portrait.fetch import get_jump_image, get_sample

def test_get_labels():
    result = run_query(query="negcon", input_column="pert_type", output_columns="*")
    print (result)
    result_df = pd.DataFrame(result)
    result_df.to_csv("../data/images/controls.csv", index=False)


@pytest.mark.parametrize(
    "s3_image_uri",
    [
        "s3://cellpainting-gallery/cpg0016-jump/source_10/images/2021_08_17_U2OS_48_hr_run16/images/Dest210809-134534/Dest210809-134534_P24_T0001F006L01A02Z01C02.tif",
        "s3://cellpainting-gallery/cpg0016-jump/source_10/images/2021_08_17_U2OS_48_hr_run16/illum/Dest210809-134534/Dest210809-134534_IllumMito.npy",
    ],
)
def test_get_image(s3_image_uri):
    assert len(get_image_from_s3uri(s3_image_uri)), "Image fetched is empty"


@pytest.mark.parametrize("gene", ["GLVAUDGFNGKCSF-UHFFFAOYSA-N"])
# @pytest.mark.parametrize("other", ["Something"])
def test_get_item_location(gene):
    # Check that finding image locations from gene or compounds works
    info = get_item_location_info(gene)

    # sub_location_df = location_df.select(
    #     ["Metadata_Source", "Metadata_Batch", "Metadata_Plate", "Metadata_Well"]).unique()
    # channel = ["DNA", "AGP", "Mito", "ER", "RNA"]  # example
    # site = [str(i) for i in range(10)]  # every site from 0 to 9 (as this is a CRISPR plate)
    # correction = "Orig"  # or "Illum"
    # verbose = False  # whether to have tqdm loading bar
    #
    # iterable, img_list = get_jump_image_batch(sub_location_df, channel, site, correction, verbose)
    print (info)
    result = info.shape
    assert result[0] > 1
    assert result[1] == 28


def is_valid_numpy_array(arr, expected_shape=None, expected_dtype=None, check_nan_inf=True):
    import numpy as np

    # Check if it's a NumPy array
    if not isinstance(arr, np.ndarray):
        return False, "Not a NumPy array."

    # Check if array is empty
    if arr.size == 0:
        return False, "Array is empty."

    # Check for NaN/Inf values
    if check_nan_inf:
        if np.isnan(arr).any():
            return False, "Array contains NaN values."
        if np.isinf(arr).any():
            return False, "Array contains infinity values."

    # Check data type
    if expected_dtype and not np.issubdtype(arr.dtype, expected_dtype):
        return False, f"Array does not have the expected dtype ({expected_dtype})."

    # Check shape
    if expected_shape and arr.shape != expected_shape:
        return False, f"Array does not have the expected shape ({expected_shape})."

    return True, "Valid NumPy array."

def download_images_for_compound(comp, location, comp_folder):
    info_location = get_item_location_info(comp)
    sub_location_df = info_location.select(location).unique()
    print(sub_location_df)
    comp_save_folder = os.path.join(comp_folder, comp)
    meta_array = download_images_for_location(comp_save_folder, sub_location_df)

    # Convert meta_array into a DataFrame and save it as a CSV file
    meta_df = pd.DataFrame(meta_array)
    meta_df.columns = ["Metadata_Source", "Metadata_Batch", "Metadata_Plate", "Metadata_Well", "Channel", "Site",
                       "Correction"]
    meta_df.to_csv(os.path.join(comp_save_folder, "meta.csv"), index=True)
    return meta_df


def download_images_for_location(file_folder, sub_location_df):
    channel = [
        "DNA",
        "AGP",
        "Mito",
        "ER",
        "RNA"
    ]
    site = [str(i) for i in range(10)]  # every site from 0 to 9 (as this is a CRISPR plate)
    correction = "Orig"  # or "Illum"
    verbose = True  # whether to have tqdm loading bar
    meta_array, img_array = get_jump_image_batch(sub_location_df, channel, site, correction, verbose)
    print(meta_array)
    print(f'length of image array is {len(img_array)}')
    assert (len(meta_array) == len(img_array))
    # Import required for directory creation
    # Create folder in the ../data/images directory using the value of comp
    # comp_folder = os.path.join("../data/images", comp)
    os.makedirs(file_folder, exist_ok=True)
    for idx, img in enumerate(img_array):
        valid_result = is_valid_numpy_array(img)
        if valid_result[0]:
            np.save(os.path.join(file_folder, f"img_{idx}.npy"), img, allow_pickle=True)
            #tiff.imwrite(os.path.join(file_folder, f"img_{idx}.tiff"), img)
        else:
            print(valid_result[1])
    return meta_array


@pytest.mark.parametrize("comp", ["ZYVXTMKTGDARKR-UHFFFAOYSA-N"])
@pytest.mark.parametrize("location", [
            ["Metadata_Source", "Metadata_Batch","Metadata_Plate", "Metadata_Well"]
            # [ "Metadata_Source" ],
            # [  "Metadata_Batch" ],
            # [  "Metadata_Plate" ],
            # [  "Metadata_Well"  ]
         ])

def test_download_images_for_item(comp, location):
    comp_folder = os.path.join("../data/images", comp)
    download_images_for_compound(comp, location, comp_folder)


def test_npy_data():

    file_path = r"C:\Development\PyRate Cell Painting\data\Images\GLVAUDGFNGKCSF-UHFFFAOYSA-N\img_1.npy"
    np_data = np.load(file_path)
    tiff.imwrite(os.path.join(os.path.dirname(file_path), f"recover.tiff"), np_data)
    print(np_data.shape)




@pytest.mark.parametrize("meta_source", [["source_8"]])
@pytest.mark.parametrize("meta_plate", [["A1170540"]])
def test_get_negative_control_locations(meta_source, meta_plate):
    info_location = get_negative_ctrl_location_for_plate(meta_source, meta_plate)
    print (info_location.columns)
    print (info_location.head(32))
    print (info_location.shape)
    # sample = get_sample()
    # source, batch, plate, well, site, *rest = sample.row(0)
    # channel = "DNA"
    # correction = None  # or "Illum"
    #
    # img = get_jump_image(source, batch, plate, well, channel, site, correction)
    
    