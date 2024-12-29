import pytest
import torch

# huggingface_openphenom_model_dir = "."
huggingface_modelpath = "recursionpharma/OpenPhenom"

from .huggingface_mae import MAEModel


@pytest.fixture
def huggingface_model():
    # This step downloads the model to a local cache, takes a bit to run
    huggingface_model = MAEModel.from_pretrained(huggingface_modelpath)
    huggingface_model.eval()
    return huggingface_model


@pytest.mark.parametrize("C", [1, 4, 6, 11])
@pytest.mark.parametrize("return_channelwise_embeddings", [True, False])
def test_model_predict(huggingface_model, C, return_channelwise_embeddings):
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
