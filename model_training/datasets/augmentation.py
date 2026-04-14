"""
Data Augmentation for COD-Odisha Training
Geometric and photometric transformations for camouflaged object detection.
"""

import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import torch
import torchvision.transforms as T
import torchvision.transforms.functional as TF


class RandomHorizontalFlip:
    """Random horizontal flip with 50% probability."""
    def __call__(self, image, mask, boundary=None):
        if random.random() < 0.5:
            image = TF.hflip(image)
            mask = TF.hflip(mask)
            if boundary is not None:
                boundary = TF.hflip(boundary)
        return image, mask, boundary


class RandomVerticalFlip:
    """Random vertical flip with 50% probability."""
    def __call__(self, image, mask, boundary=None):
        if random.random() < 0.5:
            image = TF.vflip(image)
            mask = TF.vflip(mask)
            if boundary is not None:
                boundary = TF.vflip(boundary)
        return image, mask, boundary


class RandomRotation:
    """Random rotation within specified range."""
    def __init__(self, degrees=15):
        self.degrees = degrees
    
    def __call__(self, image, mask, boundary=None):
        angle = random.uniform(-self.degrees, self.degrees)
        image = TF.rotate(image, angle, fill=0)
        mask = TF.rotate(mask, angle, fill=0)
        if boundary is not None:
            boundary = TF.rotate(boundary, angle, fill=0)
        return image, mask, boundary


class RandomCrop:
    """Random crop to specified size."""
    def __init__(self, size=(352, 352)):
        self.size = size
    
    def __call__(self, image, mask, boundary=None):
        i, j, h, w = T.RandomCrop.get_params(image, self.size)
        image = TF.crop(image, i, j, h, w)
        mask = TF.crop(mask, i, j, h, w)
        if boundary is not None:
            boundary = TF.crop(boundary, i, j, h, w)
        return image, mask, boundary


class ColorJitter:
    """Random color jittering for photometric augmentation."""
    def __init__(self, brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1):
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.hue = hue
    
    def __call__(self, image, mask, boundary=None):
        # Apply color jitter only to image, not mask
        jitter = T.ColorJitter(
            brightness=self.brightness,
            contrast=self.contrast,
            saturation=self.saturation,
            hue=self.hue
        )
        image = jitter(image)
        return image, mask, boundary


class RandomGaussianBlur:
    """Apply Gaussian blur with random probability."""
    def __init__(self, kernel_size=5, p=0.3):
        self.kernel_size = kernel_size
        self.p = p
    
    def __call__(self, image, mask, boundary=None):
        if random.random() < self.p:
            image = TF.gaussian_blur(image, self.kernel_size)
        return image, mask, boundary


class RandomNoise:
    """Add random Gaussian noise."""
    def __init__(self, std=0.01, p=0.3):
        self.std = std
        self.p = p
    
    def __call__(self, image, mask, boundary=None):
        if random.random() < self.p:
            noise = torch.randn_like(image) * self.std
            image = image + noise
            image = torch.clamp(image, 0, 1)
        return image, mask, boundary


class Compose:
    """Compose multiple augmentations."""
    def __init__(self, transforms):
        self.transforms = transforms
    
    def __call__(self, image, mask, boundary=None):
        for t in self.transforms:
            image, mask, boundary = t(image, mask, boundary)
        return image, mask, boundary


def get_train_augmentation(config=None):
    """
    Get training augmentation pipeline.
    
    Args:
        config: Optional dict with augmentation params
    """
    if config is None:
        config = {
            'horizontal_flip': True,
            'vertical_flip': False,
            'rotation_range': 15,
            'brightness': 0.2,
            'contrast': 0.2,
            'saturation': 0.2,
            'hue': 0.1,
            'random_crop': True,
            'crop_size': [352, 352]
        }
    
    transforms = []
    
    if config.get('horizontal_flip', True):
        transforms.append(RandomHorizontalFlip())
    
    if config.get('vertical_flip', False):
        transforms.append(RandomVerticalFlip())
    
    if config.get('rotation_range', 0) > 0:
        transforms.append(RandomRotation(config['rotation_range']))
    
    if config.get('random_crop', False):
        crop_size = tuple(config.get('crop_size', [352, 352]))
        transforms.append(RandomCrop(crop_size))
    
    # Color jitter (always applied but can be 0)
    transforms.append(ColorJitter(
        brightness=config.get('brightness', 0.2),
        contrast=config.get('contrast', 0.2),
        saturation=config.get('saturation', 0.2),
        hue=config.get('hue', 0.1)
    ))
    
    transforms.append(RandomGaussianBlur(p=0.2))
    
    return Compose(transforms)


def get_val_augmentation():
    """Validation augmentation - minimal processing."""
    return Compose([])
