import jump_cp_utilities as jcp_utils
import pandas as pd
import os

def download_control_images(meta_df):
    image_dir = r"../data/images/Control"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Check if Metadata_Source and Metadata_Plate columns exist
    if not all(col in meta_df.columns for col in ["Metadata_Source", "Metadata_Plate"]):
        return
    # Extract unique Metadata_Source and Metadata_Plate combinations from meta_df
    data_source_ids = meta_df[['Metadata_Source', 'Metadata_Plate']].drop_duplicates()

    # Create folders based on Metadata_Source and Metadata_Plate
    for row in data_source_ids.itertuples():
        control_plate_folder_name = os.path.join(image_dir, f"{row.Metadata_Source}_{row.Metadata_Plate}")
        if not os.path.exists(control_plate_folder_name):
            # if the control plate folder exists, means the control images have been downloaded already
            os.makedirs(control_plate_folder_name)
            location_df = jcp_utils.get_negative_ctrl_location_for_plate(row.Metadata_Source, row.Metadata_Plate).unique()
            jcp_utils.download_images_for_location(control_plate_folder_name, location_df)
            
            location_df.write_csv(os.path.join(control_plate_folder_name, "meta.csv"))






def download_dili_images(comp_file_path):
    df = pd.read_csv(comp_file_path)

    df = df.head(1)

    image_dir = r"../data/images/Dili"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    location = ["Metadata_Source", "Metadata_Batch", "Metadata_Plate", "Metadata_Well"]
    for inchi_key in df['inchi_key']:
        meta_df = jcp_utils.download_images_for_compound(inchi_key, location, image_dir)
        #meta_df = pd.read_csv(r'C:\Development\PyRate Cell Painting\data\Images\Dili\meta_single.csv')
        download_control_images(meta_df)

def test_save_negative_control_images():
    meta_file = r'C:\Development\PyRate Cell Painting\data\Images\Dili\meta.csv'
    meta_df = pd.read_csv(meta_file)
    download_control_images(meta_df)

if __name__ == "__main__":
   dili_file_path = r"../data/chembl/diliranked_compounds.csv"
   download_dili_images(dili_file_path)
   #test_save_negative_control_images()

