"""Create minimal test dataset for training validation"""

import os
from PIL import Image
import numpy as np
from pathlib import Path

# Create minimal test dataset for quick training validation
base_path = Path('data/COD10K')
base_path.mkdir(parents=True, exist_ok=True)

# Create train split
train_img_dir = base_path / 'images' / 'train'
train_gt_dir = base_path / 'gts' / 'train'
train_img_dir.mkdir(parents=True, exist_ok=True)
train_gt_dir.mkdir(parents=True, exist_ok=True)

# Create test split
test_img_dir = base_path / 'images' / 'test'
test_gt_dir = base_path / 'gts' / 'test'
test_img_dir.mkdir(parents=True, exist_ok=True)
test_gt_dir.mkdir(parents=True, exist_ok=True)

# Generate 5 dummy training images and masks
for i in range(5):
    # Create dummy color image (352x352)
    img_array = np.random.randint(0, 256, (352, 352, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(train_img_dir / f'image_{i:03d}.jpg')
    
    # Create dummy mask
    mask_array = np.random.randint(0, 2, (352, 352), dtype=np.uint8) * 255
    mask = Image.fromarray(mask_array, mode='L')
    mask.save(train_gt_dir / f'image_{i:03d}.png')

# Generate 2 dummy test images and masks
for i in range(2):
    img_array = np.random.randint(0, 256, (352, 352, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(test_img_dir / f'image_{i:03d}.jpg')
    
    mask_array = np.random.randint(0, 2, (352, 352), dtype=np.uint8) * 255
    mask = Image.fromarray(mask_array, mode='L')
    mask.save(test_gt_dir / f'image_{i:03d}.png')

print('✓ Created dummy COD10K dataset')
print(f'  Train: {len(list(train_img_dir.glob("*")))} images')
print(f'  Test: {len(list(test_img_dir.glob("*")))} images')
