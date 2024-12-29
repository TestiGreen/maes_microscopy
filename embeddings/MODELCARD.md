---
library_name: transformers
tags: []
---

# Model Card for Phenom CA-MAE-S/16

Channel-agnostic image encoding model designed for microscopy image featurization. 
The model uses a vision transformer backbone with channelwise cross-attention over patch tokens to create contextualized representations separately for each channel.


## Model Details

### Model Description

This model is a [channel-agnostic masked autoencoder](https://openaccess.thecvf.com/content/CVPR2024/html/Kraus_Masked_Autoencoders_for_Microscopy_are_Scalable_Learners_of_Cellular_Biology_CVPR_2024_paper.html) trained to reconstruct microscopy images over three datasets:
1. RxRx3
2. JUMP-CP overexpression
3. JUMP-CP gene-knockouts

- **Developed, funded, and shared by:** Recursion
- **Model type:** Vision transformer CA-MAE
- **Image modality:** Optimized for microscopy images from the CellPainting assay
- **License:** 


### Model Sources

- **Repository:** [https://github.com/recursionpharma/maes_microscopy](https://github.com/recursionpharma/maes_microscopy)
- **Paper:** [Masked Autoencoders for Microscopy are Scalable Learners of Cellular Biology](https://openaccess.thecvf.com/content/CVPR2024/html/Kraus_Masked_Autoencoders_for_Microscopy_are_Scalable_Learners_of_Cellular_Biology_CVPR_2024_paper.html)


## Uses

NOTE: model embeddings tend to extract features only after using standard batch correction post-processing techniques. **We recommend**, at a *minimum*, after inferencing the model over your images, to do the standard `PCA-CenterScale` pattern or better yet Typical Variation Normalization:

1. Fit a PCA kernel on all the *control images* (or all images if no controls) from across all experimental batches (e.g. the plates of wells from your assay),
2. Transform all the embeddings with that PCA kernel,
3. For each experimental batch, fit a separate StandardScaler on the transformed embeddings of the controls from step 2, then transform the rest of the embeddings from that batch with that StandardScaler.

### Direct Use

- Create biologically useful embeddings of microscopy images
- Create contextualized embeddings of each channel of a microscopy image (set `return_channelwise_embeddings=True`)
- Leverage the full MAE encoder + decoder to predict new channels / stains for images without all 6 CellPainting channels

### Downstream Use

- A determined ML expert could fine-tune the encoder for downstream tasks such as classification

### Out-of-Scope Use

- Unlikely to be especially performant on brightfield microscopy images
- Out-of-domain medical images, such as H&E (maybe it would be a decent baseline though)

## Bias, Risks, and Limitations

- Primary limitation is that the embeddings tend to be more useful at scale. For example, if you only have 1 plate of microscopy images, the embeddings might underperform compared to a supervised bespoke model.

## How to Get Started with the Model

You should be able to successfully run the below tests, which demonstrate how to use the model at inference time.

```python
import pytest
import torch

from embeddings.huggingface_mae import MAEModel

huggingface_phenombeta_model_dir = ".."


# huggingface_modelpath = "recursionpharma/test-pb-model"


@pytest.fixture
def huggingface_model():
    # Make sure you have the model/config downloaded from https://huggingface.co/recursionpharma/test-pb-model to this directory
    # huggingface-cli download recursionpharma/test-pb-model --local-dir=.
    huggingface_model = MAEModel.from_pretrained(huggingface_phenombeta_model_dir)
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
```


## Training, evaluation and testing details

See paper linked above for details on model training and evaluation. Primary hyperparameters are included in the repo linked above.


## Environmental Impact

- **Hardware Type:** Nvidia H100 Hopper nodes
- **Hours used:** 400
- **Cloud Provider:** private cloud
- **Carbon Emitted:** 138.24 kg co2 (roughly the equivalent of one car driving from Toronto to Montreal)

**BibTeX:**

```TeX
@inproceedings{kraus2024masked,
  title={Masked Autoencoders for Microscopy are Scalable Learners of Cellular Biology},
  author={Kraus, Oren and Kenyon-Dean, Kian and Saberian, Saber and Fallah, Maryam and McLean, Peter and Leung, Jess and Sharma, Vasudev and Khan, Ayla and Balakrishnan, Jia and Celik, Safiye and others},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={11757--11768},
  year={2024}
}
```

## Model Card Contact

- Kian Kenyon-Dean: kian.kd@recursion.com
- Oren Kraus: oren.kraus@recursion.com
- Or, email: info@rxrx.ai
