import pytest
import torch
import numpy as np
from PIL import Image

if __package__ is None or __package__ == '':
    # uses current directory visibility
    from huggingface_mae import MAEModel
    from mae_utils import unflatten_tokens
else:
    # uses current package visibility
    from .huggingface_mae import MAEModel
    from .mae_utils import unflatten_tokens

huggingface_phenombeta_model_dir = r"./"
# huggingface_modelpath = "recursionpharma/test-pb-model"

def embedding_calculator(channel_count):
    # read images and put the data in a list
    channels = []
    for i in range(1, channel_count + 1):
        im = Image.open(f"sample/AA41_s1_{i}.jp2")
        channels.append(np.array(im))

    image_array = np.stack(channels, axis=0)
    torch.tensor(image_array)
    image_tensor = crop_image(torch.tensor(image_array), channel_count)
    huggingface_model = huggingface_model_setup()
    embeddings = huggingface_model.predict(image_tensor)
    return embeddings

def crop_image(im, channel_count):
    assert im.shape == (channel_count, 512, 512)
    img = im.view(1, channel_count, 2, 256, 2, 256)
    img = img.permute(0, 2, 4, 1, 3, 5)
    return img.reshape(-1, channel_count, 256, 256)

def huggingface_model_setup():
    # Make sure you have the model/config downloaded from https://huggingface.co/recursionpharma/test-pb-model to this directory
    # huggingface-cli download recursionpharma/test-pb-model --local-dir=.
    huggingface_model = MAEModel.from_pretrained(huggingface_phenombeta_model_dir)
    huggingface_model.eval()
    return huggingface_model

def run_model_predict(huggingface_model, C, return_channelwise_embeddings):
    example_input_array = torch.randint(
        low=0,
        high=255,
        size=(2, C, 256, 256),
        dtype=torch.uint8,
        device=huggingface_model.device,
    )
    huggingface_model.return_channelwise_embeddings = return_channelwise_embeddings
    embeddings = huggingface_model.predict(example_input_array)
    expected_output_dim = 384 * C if return_channelwise_embeddings else 384
    assert embeddings.shape == (2, expected_output_dim)

if __name__ == "__main__":
    embedding_values = embedding_calculator(6)
    print(embedding_values)