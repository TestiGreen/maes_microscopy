from itertools import groupby, starmap
import pandas as pd
import numpy as np
import pytest
import tifffile as tiff  # Added for saving TIFF files
from jump_portrait.save import download_item_images
from jump_portrait.s3 import get_image_from_s3uri
from jump_portrait.fetch import  get_item_location_info, get_jump_image, get_jump_image_batch

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

@pytest.mark.parametrize("comp", ["GLVAUDGFNGKCSF-UHFFFAOYSA-N"])
@pytest.mark.parametrize("location", [
            ["Metadata_Source", "Metadata_Batch", "Metadata_Plate", "Metadata_Well"]
            # [ "Metadata_Source" ],
            # [  "Metadata_Batch" ],
            # [  "Metadata_Plate" ],
            # [  "Metadata_Well"  ]
         ])
def test_download_images_for_item(comp, location):
    info_location = get_item_location_info(comp)
    sub_location_df = info_location.select(location).unique()
    print (sub_location_df)
    channel = ["DNA", "AGP"]
    # channel = [
    #     "DNA",
    #     "AGP",
    #     "Mito",
    #     "ER",
    #     "RNA"
    # ]  # example
    site = [str(i) for i in range(10)]  # every site from 0 to 9 (as this is a CRISPR plate)
    correction = "Orig"  # or "Illum"
    verbose = True  # whether to have tqdm loading bar

    meta_array, img_array = get_jump_image_batch(sub_location_df, channel, site, correction, verbose)
    print(f"meta array length is {len(meta_array)}")
    print (f" image list length is {len(img_array)}")
    
    
    import os  # Import required for directory creation

    # Create folder in the ../data/images directory using the value of comp
    comp_folder = os.path.join("../data/images", comp)
    os.makedirs(comp_folder, exist_ok=True)
    
    # Convert meta_array into a DataFrame and save it as a CSV file
    meta_df = pd.DataFrame(meta_array)
    meta_df.to_csv(os.path.join(comp_folder, "meta.csv"), index=False)
    
    # Save the image array inside the created folder
    np.save(os.path.join(comp_folder, "img.npy"), img_array[0])
    
    # Save the first image in img_array as a TIFF file
    tiff.imwrite(os.path.join(comp_folder, "img0.tiff"), img_array[0])  # Writes .tiff file


    #download_item_images(comp, channels, corrections=corrections, controls=controls)
    assert True

