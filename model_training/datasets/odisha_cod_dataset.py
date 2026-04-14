"""
PyTorch Dataset for COD-Odisha Training
Supports CAMO, COD10K, NC4K, and custom Odisha datasets.
"""

import os
from pathlib import Path
from typing import Optional, Callable, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as T


class CODDataset(Dataset):
    """
    Camouflaged Object Detection Dataset.
    
    Expected structure:
        root/
            ├── images/
            │   ├── train/
            │   └── test/
            └── gts/ (ground truth masks)
                ├── train/
                └── test/
    """
    
    def __init__(
        self,
        root: str,
        split: str = 'train',
        transform: Optional[Callable] = None,
        image_size: Tuple[int, int] = (352, 352),
        return_boundary: bool = False
    ):
        self.root = Path(root)
        self.split = split
        self.transform = transform
        self.image_size = image_size
        self.return_boundary = return_boundary
        
        self.image_dir = self.root / 'images' / split
        self.mask_dir = self.root / 'gts' / split
        
        # Get all image files
        self.image_files = sorted([
            f for f in self.image_dir.glob('*')
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']
        ])
        
        # Verify corresponding masks exist
        self.valid_samples = []
        for img_path in self.image_files:
            mask_path = self.mask_dir / (img_path.stem + '.png')
            if mask_path.exists():
                self.valid_samples.append((img_path, mask_path))
        
        print(f"[CODDataset] Loaded {len(self.valid_samples)} samples from {root}/{split}")
    
    def __len__(self):
        return len(self.valid_samples)
    
    def __getitem__(self, idx):
        img_path, mask_path = self.valid_samples[idx]
        
        # Load image and mask
        image = Image.open(img_path).convert('RGB')
        mask = Image.open(mask_path).convert('L')
        
        # Resize
        image = image.resize(self.image_size, Image.BILINEAR)
        mask = mask.resize(self.image_size, Image.NEAREST)
        
        # Convert to tensor
        image = T.ToTensor()(image)
        mask = T.ToTensor()(mask)
        
        # Ensure mask is binary
        mask = (mask > 0.5).float()
        
        # Compute boundary if needed
        boundary = None
        if self.return_boundary:
            boundary = self._compute_boundary(mask)
        
        # Apply augmentations
        if self.transform:
            image, mask, boundary = self.transform(image, mask, boundary)
        
        sample = {
            'image': image,
            'mask': mask,
            'image_id': img_path.stem,
            'image_path': str(img_path)
        }
        
        if boundary is not None:
            sample['boundary'] = boundary
        
        return sample
    
    @staticmethod
    def _compute_boundary(mask_tensor: torch.Tensor, dilation=2) -> torch.Tensor:
        """
        Compute boundary from binary mask using dilation/erosion.
        
        Args:
            mask_tensor: [1, H, W] binary tensor
        Returns:
            boundary: [1, H, W] boundary tensor
        """
        from scipy.ndimage import binary_dilation, binary_erosion
        
        mask_np = mask_tensor.squeeze().numpy()
        
        if mask_np.sum() == 0:
            return torch.zeros_like(mask_tensor)
        
        dilated = binary_dilation(mask_np, iterations=dilation)
        eroded = binary_erosion(mask_np, iterations=dilation)
        boundary = dilated.astype(float) - eroded.astype(float)
        boundary = (boundary > 0).astype(float)
        
        return torch.from_numpy(boundary).unsqueeze(0).float()


class MultiDatasetWrapper(Dataset):
    """
    Wrapper to combine multiple COD datasets for joint training.
    e.g., CAMO + COD10K + NC4K
    """
    
    def __init__(self, datasets):
        self.datasets = datasets
        self.cumulative_sizes = []
        
        total = 0
        for ds in datasets:
            total += len(ds)
            self.cumulative_sizes.append(total)
    
    def __len__(self):
        return self.cumulative_sizes[-1]
    
    def __getitem__(self, idx):
        # Find which dataset this index belongs to
        dataset_idx = 0
        for i, cumsum in enumerate(self.cumulative_sizes):
            if idx < cumsum:
                dataset_idx = i
                if i > 0:
                    idx -= self.cumulative_sizes[i - 1]
                break
        
        return self.datasets[dataset_idx][idx]


def build_dataset(config, split='train'):
    """
    Build dataset from config.
    
    Args:
        config: Dataset configuration dict
        split: 'train' or 'test'
    """
    from .augmentation import get_train_augmentation, get_val_augmentation
    
    dataset_name = config.get('name', 'COD10K')
    image_size = tuple(config.get('image_size', [352, 352]))
    
    # Get dataset root
    paths = config.get('paths', {})
    if dataset_name == 'COD10K':
        root = paths.get('cod10k_root', './data/COD10K')
    elif dataset_name == 'CAMO':
        root = paths.get('camo_root', './data/CAMO')
    elif dataset_name == 'NC4K':
        root = paths.get('nc4k_root', './data/NC4K')
    elif dataset_name == 'OdishaCustom':
        root = paths.get('custom_odisha_root', './data/OdishaCustom')
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")
    
    # Get transforms
    if split == 'train':
        aug_config = config.get('augmentation', None)
        transform = get_train_augmentation(aug_config)
    else:
        transform = get_val_augmentation()
    
    return CODDataset(
        root=root,
        split=split,
        transform=transform,
        image_size=image_size,
        return_boundary=(split == 'train')
    )


def build_combined_dataset(config):
    """
    Build combined dataset from multiple sources.
    Useful for training on CAMO + COD10K + NC4K together.
    """
    from .augmentation import get_train_augmentation
    
    image_size = tuple(config.get('image_size', [352, 352]))
    transform = get_train_augmentation(config.get('augmentation', None))
    
    datasets = []
    paths = config.get('paths', {})
    
    # Try to load each available dataset
    for name, root_key in [
        ('CAMO', 'camo_root'),
        ('COD10K', 'cod10k_root'),
        ('NC4K', 'nc4k_root'),
        ('OdishaCustom', 'custom_odisha_root')
    ]:
        root = paths.get(root_key)
        if root and os.path.exists(root):
            try:
                ds = CODDataset(
                    root=root,
                    split='train',
                    transform=transform,
                    image_size=image_size,
                    return_boundary=True
                )
                if len(ds) > 0:
                    datasets.append(ds)
                    print(f"[MultiDataset] Added {name}: {len(ds)} samples")
            except Exception as e:
                print(f"[MultiDataset] Skipped {name}: {e}")
    
    if len(datasets) == 0:
        raise ValueError("No valid datasets found!")
    
    return MultiDatasetWrapper(datasets)
