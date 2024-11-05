import pytest
import torch

from huggingface_mae import MAEModel

huggingface_phenombeta_model_dir = "models/phenom_beta_huggingface"
# huggingface_modelpath = "recursionpharma/test-pb-model"


@pytest.fixture
def huggingface_model():
    # Make sure you have the model/config downloaded from https://huggingface.co/recursionpharma/test-pb-model to this directory
    huggingface_model = MAEModel.from_pretrained(huggingface_phenombeta_model_dir)
    huggingface_model.eval()
    return huggingface_model


@pytest.fixture
def example_input_array(huggingface_model):
    example_input_array = torch.randint(
        low=0,
        high=255,
        size=(2, 6, 256, 256),
        dtype=torch.uint8,
        device=huggingface_model.device,
    )
    return example_input_array


def test_model_predict(huggingface_model, example_input_array):
    embeddings = huggingface_model.predict(example_input_array)
    assert embeddings.shape == (2, 384)
