import pytest
import torch

from huggingface_mae import MAEModel

huggingface_phenombeta_model_dir = "models/phenom_beta_huggingface"
# huggingface_modelpath = "recursionpharma/test-pb-model"


@pytest.fixture
def huggingface_model():
    # Make sure you have the model/config downloaded from https://huggingface.co/recursionpharma/test-pb-model to this directory
    # huggingface-cli download recursionpharma/test-pb-model --local-dir=models/phenom_beta_huggingface
    huggingface_model = MAEModel.from_pretrained(huggingface_phenombeta_model_dir)
    huggingface_model.eval()
    return huggingface_model


@pytest.mark.parametrize("CHANNEL", [1, 4, 6, 11])
def test_model_predict(huggingface_model, CHANNEL):
    example_input_array = torch.randint(
        low=0,
        high=255,
        size=(2, CHANNEL, 256, 256),
        dtype=torch.uint8,
        device=huggingface_model.device,
    )
    embeddings = huggingface_model.predict(example_input_array)
    assert embeddings.shape == (2, 384)
