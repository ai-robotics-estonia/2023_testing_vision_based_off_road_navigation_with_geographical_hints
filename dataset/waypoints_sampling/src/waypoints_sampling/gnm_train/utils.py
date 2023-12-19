# pytorch
import torch
import torch.nn as nn
from torchvision import transforms

import numpy as np
from PIL import Image as PILImage
from typing import List

# models
from waypoints_sampling.gnm_train.models.gnm import GNM


def load_model(
    model_path: str,
    model_type: str,
    context: int,
    len_traj_pred: int,
    learn_angle: bool,
    obs_encoding_size: int = 1024,
    goal_encoding_size: int = 1024,
    obsgoal_encoding_size: int = 2048,
    device: torch.device = torch.device("cpu"),
) -> nn.Module:
    """Load a model from a checkpoint file (works with models trained on multiple GPUs)"""
    checkpoint = torch.load(model_path, map_location=device)
    loaded_model = checkpoint["model"]
    if model_type == "gnm":
        model = GNM(
            context,
            len_traj_pred,
            learn_angle,
            obs_encoding_size,
            goal_encoding_size,
        )
    else:
        raise ValueError(f"Invalid model type: {model_type}")
    try:
        state_dict = loaded_model.module.state_dict()
        model.load_state_dict(state_dict)
    except AttributeError as e:
        state_dict = loaded_model.state_dict()
        model.load_state_dict(state_dict)
    model.to(device)
    return model


def to_numpy(tensor):
    return tensor.cpu().detach().numpy()


def transform_images(
    pil_imgs: List[PILImage.Image], image_size: List[int]
) -> torch.Tensor:
    """
    Transforms a list of PIL image to a torch tensor.
    Args:
        pil_imgs (List[PILImage.Image]): List of PIL images to transform and concatenate
        image_size (int, int): Size of the output image [width, height]
    """
    assert len(image_size) == 2
    image_size = image_size[::-1] # torchvision's transforms.Resize expects [height, width]
    transform_type = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Resize(image_size),  
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    if type(pil_imgs) != list:
        pil_imgs = [pil_imgs]
    transf_imgs = []
    for pil_img in pil_imgs:
        transf_img = transform_type(pil_img)
        transf_img = torch.unsqueeze(transf_img, 0)
        transf_imgs.append(transf_img)
    return torch.cat(transf_imgs, dim=1)
