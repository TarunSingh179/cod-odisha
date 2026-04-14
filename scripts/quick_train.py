#!/usr/bin/env python3
"""
Quick start training script for COD-Odisha
Uses absolute paths to ensure dataset loading works from any directory
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Get absolute dataset path
dataset_root = Path(__file__).parent / 'data' / 'COD10K'
dataset_root = dataset_root.resolve()

print(f"Dataset root: {dataset_root}")
print(f"Train images exist: {(dataset_root / 'images' / 'train').exists()}")
print(f"Test images exist: {(dataset_root / 'images' / 'test').exists()}")

# Import and run training
from backend.app.models import build_model
from model_training.datasets.odisha_cod_dataset import CODDataset
from model_training.datasets.augmentation import get_train_augmentation, get_val_augmentation

import torch
from torch.utils.data import DataLoader

print("\n" + "="*60)
print("COD-Odisha Quick Training")
print("="*60)

# Build model
model = build_model(backbone='resnet50', pretrained=True)
device = torch.device('cpu')  # Use CPU for testing
model = model.to(device)
print(f"Model loaded: {model.backbone_name}")

# Build dataset
train_aug = get_train_augmentation()
train_dataset = CODDataset(
    root=str(dataset_root),
    split='train',
    transform=train_aug,
    image_size=(352, 352),
    return_boundary=True
)
print(f"Train dataset: {len(train_dataset)} samples")

val_aug = get_val_augmentation()
val_dataset = CODDataset(
    root=str(dataset_root),
    split='test',
    transform=val_aug,
    image_size=(352, 352),
    return_boundary=False
)
print(f"Val dataset: {len(val_dataset)} samples")

if len(train_dataset) == 0 or len(val_dataset) == 0:
    print("\nError: No samples found in dataset!")
    sys.exit(1)

# Create dataloaders
train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=2, shuffle=False, num_workers=0)

print(f"Train batches: {len(train_loader)}")
print(f"Val batches: {len(val_loader)}")

# Test single forward pass
print("\nTesting forward pass...")
batch = next(iter(train_loader))
images = batch['image'].to(device)
masks = batch['mask'].to(device)

print(f"Input shape: {images.shape}")
print(f"Mask shape: {masks.shape}")

with torch.no_grad():
    output = model(images, target_mask=masks)
    print(f"Output mask shape: {output['mask'].shape}")
    print(f"Loss: {output['losses']['total']:.4f}")

print("\n✓ Training setup successful! Model is ready for training.")
print("=" * 60)
