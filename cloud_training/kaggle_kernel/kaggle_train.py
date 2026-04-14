#!/usr/bin/env python3
"""
COD-Odisha Cloud Training Script  Kaggle Notebooks
=====================================================

Instructions:
  1. Go to https://www.kaggle.com  New Notebook
  2. Add the COD10K dataset to your notebook:
     - Click "Add Data"  Search "COD10K"  Add
  3. Under Settings  Accelerator  Select "GPU P100"
  4. Paste this script into a cell and run

Kaggle gives you:
  - Free P100 GPU (16GB)
  - 30 hours/week of GPU time
  - Persistent /kaggle/working/ output directory
"""

import os
import sys
import time
import json
import shutil
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import torchvision.transforms as T
import numpy as np

# ============================================================
# KAGGLE-SPECIFIC CONFIGURATION
# ============================================================

KAGGLE_CONFIG = {
    'backbone': 'resnet50',
    'epochs': 100,
    'batch_size': 12,              # P100 has 16GB  can handle larger batches
    'lr': 1e-4,
    'weight_decay': 0.01,
    'image_size': (352, 352),
    'mixed_precision': True,
    'gradient_clip': 1.0,
    'log_interval': 25,
    'save_interval': 10,
    'num_workers': 4,              # Kaggle has 4 CPU cores
}

# Kaggle dataset paths  update this if your dataset has a different name
KAGGLE_DATA_PATHS = [
    '/kaggle/input/cod10k',
    '/kaggle/input/cod10k-dataset',
    '/kaggle/input/camouflaged-object-detection-cod10k',
]

OUTPUT_DIR = Path('/kaggle/working/cod-odisha-output')


def find_kaggle_data():
    """Find COD10K dataset in Kaggle's input directory."""
    print("  [DEBUG] Checking what Kaggle mounted in /kaggle/input:")
    input_dir = Path('/kaggle/input')
    if input_dir.exists():
        for item in input_dir.iterdir():
            print(f"    - {item}")
            if item.is_dir():
                for sub in item.iterdir():
                    print(f"      - {sub}")
    else:
        print("    /kaggle/input does not exist!")

    # Check standard Kaggle input paths
    for path in KAGGLE_DATA_PATHS:
        p = Path(path)
        if p.exists():
            print(f"  [SUCCESS] Found dataset at: {p}")
            return p
    
    # Aggressive search: look for any .jpg file, then find its dataset root
    if input_dir.exists():
        print("  [DEBUG] Doing aggressive recursive search for dataset root...")
        for img_path in input_dir.rglob('*.jpg'):
            for parent in img_path.parents:
                # Layout 1: images & gts
                if (parent / 'images').exists() and (parent / 'gts').exists():
                    print(f"  [SUCCESS] Found dataset recursively at: {parent}")
                    return parent
                # Layout 2: Train_Image
                if any(parent.glob('Train_Image*')) or any(parent.glob('Train_GT*')):
                    print(f"  [SUCCESS] Found CAMO/Test layout at: {parent}")
                    return parent
                    
        # Fallback Search all input directories
        for d in input_dir.iterdir():
            if d.is_dir():
                # Check if it has images subdirectory
                if (d / 'images').exists() or (d / 'Image').exists() or any(d.rglob('Train_Image')) or any(d.rglob('Train_GT')):
                    print(f"  [SUCCESS] Found dataset at: {d}")
                    return d
    
    # Fallback to local path
    local = Path('./data/COD10K')
    if local.exists():
        return local
    
    return None


def prepare_kaggle_dataset(kaggle_data_path):
    """
    Organize Kaggle dataset into expected structure.
    Kaggle datasets may have different internal layouts.
    """
    data_root = Path('/kaggle/working/data/COD10K')
    
    # Check if already organized
    if (data_root / 'images' / 'train').exists():
        train_count = len(list((data_root / 'images' / 'train').glob('*')))
        if train_count > 0:
            print(f"   Dataset already organized: {train_count} training images")
            return data_root
    
    print("   Organizing dataset...")
    for split in ['train', 'test']:
        (data_root / 'images' / split).mkdir(parents=True, exist_ok=True)
        (data_root / 'gts' / split).mkdir(parents=True, exist_ok=True)
    
    # Common COD10K layouts
    source = Path(kaggle_data_path)
    
    # Layout 1: images/train, gts/train (already correct)
    if (source / 'images' / 'train').exists():
        for split in ['train', 'test']:
            src_img = source / 'images' / split
            src_gt = source / 'gts' / split
            if src_img.exists():
                _copy_images(src_img, data_root / 'images' / split)
            if src_gt.exists():
                _copy_images(src_gt, data_root / 'gts' / split)
    
    # Layout 2: Train_Image, Test_Image, etc.
    elif (source / 'Train_Image').exists() or any(source.rglob('Train_Image')):
        search = source
        for d in source.rglob('Train_Image'):
            search = d.parent
            break
        
        mapping = {
            'Train_Image': ('images', 'train'),
            'Test_Image': ('images', 'test'),
            'Train_GT': ('gts', 'train'),
            'Test_GT': ('gts', 'test'),
        }
        for src_name, (dst_type, dst_split) in mapping.items():
            src = search / src_name
            if src.exists():
                _copy_images(src, data_root / dst_type / dst_split)
    
    # Layout 3: CAMO/COD10K structure with CAM subdirs
    else:
        # Try to find image directories recursively
        for img_dir in source.rglob('*'):
            if img_dir.is_dir():
                name_lower = img_dir.name.lower()
                parent_lower = img_dir.parent.name.lower() if img_dir.parent else ''
                
                if ('train' in name_lower or 'train' in parent_lower) and 'image' in name_lower:
                    _copy_images(img_dir, data_root / 'images' / 'train')
                elif ('test' in name_lower or 'test' in parent_lower) and 'image' in name_lower:
                    _copy_images(img_dir, data_root / 'images' / 'test')
                elif ('train' in name_lower or 'train' in parent_lower) and ('gt' in name_lower or 'mask' in name_lower):
                    _copy_images(img_dir, data_root / 'gts' / 'train')
                elif ('test' in name_lower or 'test' in parent_lower) and ('gt' in name_lower or 'mask' in name_lower):
                    _copy_images(img_dir, data_root / 'gts' / 'test')
    
    # Report
    for split in ['train', 'test']:
        img_count = len(list((data_root / 'images' / split).glob('*')))
        gt_count = len(list((data_root / 'gts' / split).glob('*')))
        print(f"  {split}: {img_count} images, {gt_count} masks")
    
    return data_root


def _copy_images(src, dst):
    """Copy image files from src to dst."""
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob('*'):
        if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            shutil.copy2(str(f), str(dst / f.name))


# ============================================================
# MODEL ARCHITECTURE (same as colab_train.py)
# ============================================================

class ChannelAttention(nn.Module):
    def __init__(self, in_channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // reduction, 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // reduction, in_channels, 1)
        )
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        return self.sigmoid(self.fc(self.avg_pool(x)) + self.fc(self.max_pool(x)))


class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=kernel_size // 2)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out = torch.max(x, dim=1, keepdim=True)[0]
        return self.sigmoid(self.conv(torch.cat([avg_out, max_out], dim=1)))


class CCSIM(nn.Module):
    def __init__(self, in_channels, out_channels=128):
        super().__init__()
        self.aligns = nn.ModuleList([nn.Conv2d(c, out_channels, 1) for c in in_channels])
        self.cas = nn.ModuleList([ChannelAttention(out_channels) for _ in in_channels])
        self.interaction = nn.Sequential(
            nn.Conv2d(out_channels * 4, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels)
        )
    
    def forward(self, features):
        aligned = [a(f) * ca(a(f)) for f, a, ca in zip(features, self.aligns, self.cas)]
        h, w = aligned[0].shape[-2:]
        resized = [aligned[0]] + [F.interpolate(a, (h, w), mode='bilinear', align_corners=False) for a in aligned[1:]]
        return self.interaction(torch.cat(resized, dim=1))


class SGFL(nn.Module):
    def __init__(self, in_channels, out_channels=64):
        super().__init__()
        def branch():
            return nn.Sequential(
                nn.Conv2d(in_channels, in_channels // 2, 3, padding=1),
                nn.BatchNorm2d(in_channels // 2), nn.ReLU(inplace=True),
                nn.Conv2d(in_channels // 2, out_channels, 3, padding=1),
                nn.BatchNorm2d(out_channels)
            )
        self.semantic = branch()
        self.object_b = branch()
        self.boundary = branch()
        self.ca = ChannelAttention(out_channels)
        self.sa = SpatialAttention()
    
    def forward(self, x):
        c = self.semantic(x) + self.object_b(x) + self.boundary(x)
        return c * self.ca(c) * self.sa(c * self.ca(c))


class BoundaryAwareDecoder(nn.Module):
    def __init__(self, in_channels=64):
        super().__init__()
        self.d4 = nn.Sequential(nn.Conv2d(in_channels, in_channels, 3, padding=1), nn.BatchNorm2d(in_channels), nn.ReLU(True))
        self.d3 = nn.Sequential(nn.Conv2d(in_channels, in_channels//2, 3, padding=1), nn.BatchNorm2d(in_channels//2), nn.ReLU(True))
        self.d2 = nn.Sequential(nn.Conv2d(in_channels//2, in_channels//4, 3, padding=1), nn.BatchNorm2d(in_channels//4), nn.ReLU(True))
        self.mask_head = nn.Conv2d(in_channels // 4, 1, 1)
        self.boundary_head = nn.Conv2d(in_channels // 4, 1, 1)
    
    def forward(self, x, target_size=None):
        for d in [self.d4, self.d3, self.d2]:
            x = F.interpolate(d(x), scale_factor=2, mode='bilinear', align_corners=False)
        mask = torch.sigmoid(self.mask_head(x))
        boundary = torch.sigmoid(self.boundary_head(x))
        if target_size:
            mask = F.interpolate(mask, target_size, mode='bilinear', align_corners=False)
            boundary = F.interpolate(boundary, target_size, mode='bilinear', align_corners=False)
        return {'mask': mask, 'boundary': boundary, 'confidence': mask.max(-1)[0].max(-1)[0]}


class CODModel(nn.Module):
    def __init__(self, backbone='resnet50', pretrained=True, ccsim_out=128, sgfl_out=64):
        super().__init__()
        if backbone == 'resnet50':
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            resnet = models.resnet50(weights=weights)
            channels = [256, 512, 1024, 2048]
        else:
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            resnet = models.resnet18(weights=weights)
            channels = [64, 128, 256, 512]
        
        self.layer1 = nn.Sequential(resnet.conv1, resnet.bn1, resnet.relu, resnet.maxpool)
        self.layer2, self.layer3, self.layer4, self.layer5 = resnet.layer1, resnet.layer2, resnet.layer3, resnet.layer4
        self.ccsim = CCSIM(channels, ccsim_out)
        self.sgfl = SGFL(ccsim_out, sgfl_out)
        self.decoder = BoundaryAwareDecoder(sgfl_out)
        self.loss_weights = {'bce': 1.0, 'iou': 1.0, 'boundary': 0.5, 'semantic': 0.3}
    
    def forward(self, x, target_mask=None, target_boundary=None):
        size = x.shape[-2:]
        c1 = self.layer1(x)
        c2, c3, c4, c5 = self.layer2(c1), self.layer3(self.layer2(c1)), None, None
        # Proper sequential forward
        c2 = self.layer2(c1)
        c3 = self.layer3(c2)
        c4 = self.layer4(c3)
        c5 = self.layer5(c4)
        out = self.decoder(self.sgfl(self.ccsim([c2, c3, c4, c5])), size)
        if target_mask is not None:
            out['losses'] = self._losses(out['mask'], target_mask, target_boundary)
        return out
    
    def _losses(self, pred, target, boundary=None):
        bce = F.binary_cross_entropy(pred, target)
        inter = (pred * target).sum()
        union = (pred + target - pred * target).sum()
        iou = 1 - (inter + 1e-8) / (union + 1e-8)
        bl = F.binary_cross_entropy(pred, boundary) * 0.5 if boundary is not None else torch.tensor(0.0, device=pred.device)
        edge_k = torch.tensor([[-1.,0.,1.],[-2.,0.,2.],[-1.,0.,1.]]).view(1,1,3,3).to(pred.device)
        sem = 1.0 - torch.abs(F.conv2d(pred, edge_k, padding=1)).mean()
        total = self.loss_weights['bce']*bce + self.loss_weights['iou']*iou + self.loss_weights['boundary']*bl + self.loss_weights['semantic']*sem
        return {'bce': bce, 'iou': iou, 'boundary': bl, 'semantic': sem, 'total': total}


# ============================================================
# DATASET
# ============================================================

class CODDataset(Dataset):
    def __init__(self, root, split='train', image_size=(352, 352), augment=False):
        self.root, self.image_size, self.augment = Path(root), image_size, augment
        img_dir = self.root / 'images' / split
        mask_dir = self.root / 'gts' / split
        imgs = sorted(f for f in img_dir.glob('*') if f.suffix.lower() in ['.jpg','.jpeg','.png','.bmp'])
        self.samples = []
        for im in imgs:
            for ext in ['.png', '.jpg']:
                mp = mask_dir / (im.stem + ext)
                if mp.exists():
                    self.samples.append((im, mp)); break
        print(f"  [{split}] {len(self.samples)} samples")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        ip, mp = self.samples[idx]
        img = T.ToTensor()(Image.open(ip).convert('RGB').resize(self.image_size, Image.BILINEAR))
        mask = (T.ToTensor()(Image.open(mp).convert('L').resize(self.image_size, Image.NEAREST)) > 0.5).float()
        if self.augment and torch.rand(1) < 0.5:
            img, mask = torch.flip(img, [2]), torch.flip(mask, [2])
        # Boundary
        from scipy.ndimage import binary_dilation, binary_erosion
        m = mask.squeeze().numpy()
        if m.sum() > 0:
            bd = (binary_dilation(m, iterations=2).astype(float) - binary_erosion(m, iterations=2).astype(float) > 0).astype(float)
            boundary = torch.from_numpy(bd).unsqueeze(0).float()
        else:
            boundary = torch.zeros_like(mask)
        return {'image': img, 'mask': mask, 'boundary': boundary}


# ============================================================
# TRAINING
# ============================================================

def main():
    print("=" * 70)
    print("  COD-Odisha -- Kaggle Training")
    print("=" * 70)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}" + (f" ({torch.cuda.get_device_name(0)})" if torch.cuda.is_available() else ""))
    
    # Find and prepare dataset
    kaggle_data = find_kaggle_data()
    if kaggle_data is None:
        print("   No dataset found! Add COD10K dataset to your Kaggle notebook.")
        print("     Click 'Add Data'  Search 'COD10K'  Add")
        return
    
    data_root = prepare_kaggle_dataset(kaggle_data)
    
    # Build model
    model = CODModel('resnet50', pretrained=True).to(device)
    print(f"  Model params: {sum(p.numel() for p in model.parameters())/1e6:.1f}M")
    
    # Datasets
    train_ds = CODDataset(str(data_root), 'train', augment=True)
    val_ds = CODDataset(str(data_root), 'test', augment=False)
    
    cfg = KAGGLE_CONFIG
    train_dl = DataLoader(train_ds, cfg['batch_size'], shuffle=True, num_workers=cfg['num_workers'], pin_memory=True, drop_last=True)
    val_dl = DataLoader(val_ds, cfg['batch_size'], shuffle=False, num_workers=cfg['num_workers'], pin_memory=True)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg['lr'], weight_decay=cfg['weight_decay'])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, cfg['epochs'], eta_min=1e-6)
    scaler = torch.amp.GradScaler('cuda') if cfg['mixed_precision'] and device.type == 'cuda' else None
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    best_metric = 0
    
    print(f"\n Training for {cfg['epochs']} epochs...")
    
    for epoch in range(cfg['epochs']):
        model.train()
        total_loss, n = 0, 0
        t0 = time.time()
        
        for i, batch in enumerate(train_dl):
            imgs = batch['image'].to(device)
            masks = batch['mask'].to(device)
            bounds = batch['boundary'].to(device)
            
            optimizer.zero_grad()
            if scaler:
                with torch.amp.autocast('cuda'):
                    out = model(imgs, masks, bounds)
                    loss = out['losses']['total']
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), cfg['gradient_clip'])
                scaler.step(optimizer)
                scaler.update()
            else:
                out = model(imgs, masks, bounds)
                loss = out['losses']['total']
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), cfg['gradient_clip'])
                optimizer.step()
            
            total_loss += loss.item()
            n += 1
            
            if i % cfg['log_interval'] == 0:
                print(f"  E{epoch+1} [{i}/{len(train_dl)}] Loss: {total_loss/n:.4f}")
        
        scheduler.step()
        
        # Validate
        model.eval()
        preds, gts = [], []
        with torch.no_grad():
            for batch in val_dl:
                o = model(batch['image'].to(device))
                preds.append(o['mask'].cpu().numpy())
                gts.append(batch['mask'].numpy())
        
        p, g = np.concatenate(preds).flatten(), np.concatenate(gts).flatten()
        mae = float(np.mean(np.abs(p - g)))
        pb = (p > 0.5).astype(float)
        tp, fp, fn = np.sum(pb*g), np.sum(pb*(1-g)), np.sum((1-pb)*g)
        prec, rec = float(tp/(tp+fp+1e-8)), float(tp/(tp+fn+1e-8))
        fm = float(1.3*prec*rec/(0.3*prec+rec+1e-8))
        
        dt = time.time() - t0
        print(f"  Epoch {epoch+1}/{cfg['epochs']} ({dt:.0f}s) | Loss: {total_loss/n:.4f} | F: {fm:.4f} | MAE: {mae:.4f}")
        
        if fm > best_metric:
            best_metric = fm
            torch.save({'epoch': epoch+1, 'model_state_dict': model.state_dict(), 'best_metric': float(best_metric)},
                       str(OUTPUT_DIR / 'best_model.pth'))
            print(f"   Best model saved (F={best_metric:.4f})")
        
        if (epoch+1) % cfg['save_interval'] == 0:
            torch.save({'epoch': epoch+1, 'model_state_dict': model.state_dict()},
                       str(OUTPUT_DIR / f'ckpt_e{epoch+1}.pth'))
    
    print(f"\n Done! Best F-measure: {best_metric:.4f}")
    print(f"   Models saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
