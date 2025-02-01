import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

if __package__ is None or __package__ == '':
    # uses current directory visibility
    from huggingface_mae import MAEModel
else:
    # uses current package visibility
    from .huggingface_mae import MAEModel

huggingface_phenombeta_model_dir = r"./"

def huggingface_model_setup():
    # Make sure you have the model/config downloaded from https://huggingface.co/recursionpharma/test-pb-model to this directory
    # huggingface-cli download recursionpharma/test-pb-model --local-dir=.
    huggingface_model = MAEModel.from_pretrained(huggingface_phenombeta_model_dir)
    huggingface_model.eval()
    return huggingface_model

#TODO:  loop through the folder in the file_dir to process .npy files. Extract the source name, plate name, well name, and site name from the file names.
#TODO:  Assert that the source and plate names are consistent across all files, as requested.
#TODO:  Group .npy files together if their well and site names match before further processing.
#TODO:  Split each site image into `n*256*256` crops to prepare smaller image patches for processing.
#TODO:  Pass the array of image crops through the inference model, averaging the output embeddings to create one embedding per well.
#TODO:  Save the resulting average embeddings for each well to properly store the processed data.

class ImageDataset(Dataset):
        def __init__(self, file_dir):
            # Step 1: Validate and group files by well and site
            site_images = {}
            for file in os.listdir(file_dir):
                file_name, file_extension = os.path.splitext(file)

                if file_extension != '.npy':
                    continue

                parts = file_name.split('_')
                assert len(parts) >= 4, f"Filename {file} is invalid"
                plate, well, site = parts[-4], parts[-3], parts[-2]
                # source = "_".join(parts[:-4])  # Don't need this now, but maybe in future

                # Group by well and site
                key = (well, site)
                if key not in site_images:
                    site_images[key] = []
                site_images[key].append(file)

            self.data: dict[str, list[Path]] = {}
            self._channel_count = None
            self._site_count = 0

            first_well = None
            for (well, site), files in site_images.items():
                if well not in self.data:
                    self.data[well] = []
                if first_well is None:
                    first_well = well

                for file in files:
                    self.data[well].append(Path(file_dir, file))

                if self._channel_count is None:
                    self._channel_count = len(files)
                if first_well == well:
                    self._site_count = self._site_count + 1



        def __len__(self):
            return len(self.data)

        def __getitem__(self, idx) -> tuple[str, list[Path]]:
            """
            Gets the well name and list of (site, file path) tuples for the given index.
            """
            well = list(self.data)[idx]
            return well, self.data[well]

        @property
        def well_count(self):
            return len(self.data)

        @property
        def sites_per_well(self):
            return self._site_count

        @property
        def channel_count(self):
            return self._channel_count


# mae_openphenomon model only support tile size 256
tile_size = 256
tile_count = 4
feature_count = 384
batch_size = 1


def generate_image_embeddings(model, file_dir):
    """
    This function processes image data from .npy files, organizes them by well and site, 
    splits them into smaller crops, performs inference on the crops, and stores averaged embeddings.

    Params:
        file_dir (str): Directory containing .npy files to process.
    """

    # def embedding_calculator(channel_count, image_array):
    #     torch.tensor(image_array)
    #     image_tensor = crop_image(torch.tensor(image_array), channel_count)
    #
    #     embeddings = model.predict(image_tensor)
    #     return embeddings

   

    # Step 2: Split images into `n*256*256` crops
    # def split_image_into_crops(image, crop_height=256, crop_width=256):
    #     img_height, img_width = image.shape[:2]
    #     crops = []
    #     for y in range(0, img_height, crop_height):
    #         for x in range(0, img_width, crop_width):
    #             crop = image[y:y + crop_height, x:x + crop_width]
    #             if crop.shape == (crop_height, crop_width, image.shape[2]):  # Check if crop has correct dimensions
    #                 crops.append(crop)
    #     return np.array(crops)

    dataset = ImageDataset(file_dir)

    def crop_image(im):
        im = im[:, :, :tile_count * tile_size, :tile_count * tile_size]  # Ignore pixels exceeding 4 tiles
        height, width = im.shape[-2], im.shape[-1]
        stride_h = max(1, (height - tile_size) // (tile_count-1))  # Calculate stride for minimum overlap
        stride_w = max(1, (width  - tile_size) // (tile_count-1))  # Calculate stride for minimum overlap
        crops = []
        for     h in range(0, height - tile_size + 1, stride_h):
            for w in range(0, width  - tile_size + 1, stride_w):
                crops.append(im[:, :, h:h + tile_size, w:w + tile_size])
        return np.stack(crops)  # Stack crops into a tensor

    def collate_fn(batch):  # Simplified collate_fn
        wells, image_paths_per_well = zip(*batch)
        # Assert the length of each item's file list is a multiple of channel_count
        for image_paths_one_well in image_paths_per_well:
            assert len(image_paths_one_well) % dataset.channel_count == 0, "Invalid channel count in file list."

        # Load, process, and crop each file
        batch_images = []
        for image_paths_one_well in image_paths_per_well:
            well_images = []
            for image_path in image_paths_one_well:
                data = np.load(image_path)
                well_images.append(data)
            assert all(
                item.shape == well_images[0].shape for item in
                well_images), "Shapes of all files in a site must be the same"
            batch_images.append(np.stack(well_images))
        np_batch_images = np.stack(batch_images)

        # We have:
        #     Well,site*channel,h,w
        # We need:
        #     Well*Site,Channel,h,w


        np_batch_images = np_batch_images.reshape(-1, dataset.channel_count, np_batch_images.shape[-2], np_batch_images.shape[-1])

        # After Crop we need:
        #     Well*Site,16,Channel,h,w
        cropped_images = np.vstack(crop_image(np_batch_images))  # convert to 4 256x256 patches
        # We want to return:
        #     Well,Site*16,Channel,h,w
        batch_cropped_images = cropped_images.reshape(len(wells), -1, dataset.channel_count, tile_size, tile_size )
        return wells, torch.from_numpy(batch_cropped_images)

    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)  # Adjust batch size as needed

    # Inference loop
    well_ids = []
    emb_ind = 0

    num_images = (tile_count * tile_count) * dataset.well_count * dataset.sites_per_well * dataset.channel_count
    embeddings = np.zeros(
        (num_images, feature_count), dtype=np.float32
    )

    forward_pass_counter = 0
    for well_ids, batch_tensors in dataloader:
        well_count, location_count, channel_count, _, _ = batch_tensors.shape
        batch_tensors = batch_tensors.reshape(-1, channel_count, tile_size, tile_size)
        print(batch_tensors.shape)
        latent = model.predict(batch_tensors)
        latent = latent.reshape(len(well_ids), -1, feature_count)
        print(latent.shape)

        latent = latent.view(-1, location_count, feature_count).mean(dim=1)  # average over all 256x256 location imgs per well
        print(latent.shape)
        embeddings[emb_ind: (emb_ind + len(latent))] = latent.detach().cpu().numpy()

        emb_ind += len(latent)
        forward_pass_counter += 1
        if forward_pass_counter % 5 == 0:
            print(
                f"forward pass {forward_pass_counter} of {len(dataloader)} done, wells inferenced {emb_ind}")

    embedding_df = embeddings[:emb_ind]
    embedding_df = pd.DataFrame(embedding_df)
    embedding_df.columns = [f"feature_{i}" for i in range(feature_count)]
    embedding_df['well_id'] = well_ids
    embedding_df = embedding_df[['well_id'] + [f"feature_{i}" for i in range(feature_count)]]
    embedding_df.to_parquet('jumpCP_embeddings.parquet')


if __name__ == "__main__":
    file_dir = r"D:\Project\PyRate\data\images\Control"
    model = huggingface_model_setup()
    for dir in os.listdir(file_dir):
        item_path = os.path.join(file_dir, dir)
        if os.path.isdir(item_path):
            generate_image_embeddings(model, item_path)
