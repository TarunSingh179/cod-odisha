"""
COD-Odisha Training Script

Trains the camouflaged object detection model using CCSIM + SGFL architecture.
Supports mixed precision, multi-dataset training, and comprehensive logging.

Usage:
    python train.py --config configs/resnet50_config.yaml
"""

import os
import argparse
import yaml
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.amp import autocast, GradScaler
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.models import build_model
from model_training.datasets.odisha_cod_dataset import build_dataset, build_combined_dataset


class MetricTracker:
    """Track training metrics."""
    def __init__(self):
        self.metrics = {}
        self.counts = {}
    
    def update(self, key, value):
        if key not in self.metrics:
            self.metrics[key] = 0
            self.counts[key] = 0
        self.metrics[key] += value
        self.counts[key] += 1
    
    def get(self, key):
        if key not in self.metrics:
            return 0
        return self.metrics[key] / self.counts[key]
    
    def reset(self):
        self.metrics.clear()
        self.counts.clear()
    
    def summary(self):
        return {k: self.get(k) for k in self.metrics.keys()}


def train_epoch(model, dataloader, optimizer, scaler, device, config):
    """Train for one epoch."""
    model.train()
    tracker = MetricTracker()
    
    use_amp = config['training'].get('mixed_precision', True)
    grad_clip = config['training'].get('gradient_clip', 1.0)
    
    for batch_idx, batch in enumerate(dataloader):
        images = batch['image'].to(device)
        masks = batch['mask'].to(device)
        boundaries = batch.get('boundary', None)
        if boundaries is not None:
            boundaries = boundaries.to(device)
        
        optimizer.zero_grad()
        
        # Forward pass with optional AMP
        with autocast('cuda', enabled=use_amp):
            outputs = model(images, target_mask=masks, target_boundary=boundaries)
            losses = outputs['losses']
            loss = losses['total']
        
        # Backward pass
        if use_amp:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            
            # Gradient clipping
            if grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            if grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()
        
        # Track metrics
        tracker.update('loss', loss.item())
        tracker.update('bce', losses['bce'].item())
        tracker.update('iou', losses['iou'].item())
        
        if batch_idx % config['logging'].get('log_interval', 50) == 0:
            print(f"  Batch {batch_idx}/{len(dataloader)}: "
                  f"Loss={tracker.get('loss'):.4f}, "
                  f"BCE={tracker.get('bce'):.4f}, "
                  f"IoU={tracker.get('iou'):.4f}")
    
    return tracker.summary()


@torch.no_grad()
def validate(model, dataloader, device):
    """Validate model and compute metrics."""
    model.eval()
    tracker = MetricTracker()
    
    all_preds = []
    all_gts = []
    
    for batch in dataloader:
        images = batch['image'].to(device)
        masks = batch['mask'].to(device)
        
        outputs = model(images)
        preds = outputs['mask']
        
        # Collect for metric computation
        all_preds.append(preds.cpu().numpy())
        all_gts.append(masks.cpu().numpy())
        
        tracker.update('confidence', outputs['confidence'].mean().item())
    
    # Compute evaluation metrics
    all_preds = np.concatenate(all_preds, axis=0)
    all_gts = np.concatenate(all_gts, axis=0)
    
    metrics = compute_metrics(all_preds, all_gts)
    metrics['confidence'] = tracker.get('confidence')
    
    return metrics


def compute_metrics(pred, gt):
    """
    Compute COD evaluation metrics.
    
    Metrics:
        - S-measure (Structure measure)
        - E-measure (Enhanced alignment measure)
        - F-measure (F-beta score)
        - MAE (Mean Absolute Error)
    """
    pred = pred.flatten()
    gt = gt.flatten()
    
    # MAE
    mae = np.mean(np.abs(pred - gt))
    
    # F-measure
    pred_binary = (pred > 0.5).astype(float)
    tp = np.sum(pred_binary * gt)
    fp = np.sum(pred_binary * (1 - gt))
    fn = np.sum((1 - pred_binary) * gt)
    
    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f_measure = 1.3 * precision * recall / (0.3 * precision + recall + 1e-8)
    
    # Approximate S-measure (simplified)
    s_measure = 1 - mae
    
    return {
        'mae': float(mae),
        'f_measure': float(f_measure),
        's_measure': float(s_measure),
        'precision': float(precision),
        'recall': float(recall)
    }


def main():
    parser = argparse.ArgumentParser(description='Train COD-Odisha model')
    parser.add_argument('--config', type=str, required=True, help='Path to config YAML')
    parser.add_argument('--resume', type=str, default=None, help='Resume from checkpoint')
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    print("=" * 60)
    print("COD-Odisha Training")
    print("=" * 60)
    print(f"Config: {args.config}")
    print(f"Model: {config['model']['backbone']}")
    print(f"Epochs: {config['training']['epochs']}")
    print(f"Batch size: {config['training']['batch_size']}")
    print("=" * 60)
    
    # Setup device
    device = torch.device('cuda' if config['device'].get('use_cuda', True) and torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    
    # Build model
    model = build_model(
        backbone=config['model']['backbone'],
        pretrained=config['model'].get('pretrained', True)
    )
    model = model.to(device)
    
    if torch.cuda.device_count() > 1:
        print(f"Using {torch.cuda.device_count()} GPUs")
        model = nn.DataParallel(model)
    
    # Build datasets
    print("\n[Dataset] Loading training data...")
    try:
        train_dataset = build_combined_dataset(config['dataset'])
    except ValueError:
        train_dataset = build_dataset(config['dataset'], split='train')
    
    print("[Dataset] Loading validation data...")
    val_dataset = build_dataset(config['dataset'], split='test')
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True,
        num_workers=config['training'].get('num_workers', 4),
        pin_memory=True,
        drop_last=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False,
        num_workers=config['training'].get('num_workers', 4),
        pin_memory=True
    )
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    
    # Optimizer and scheduler
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config['training']['optimizer']['lr'],
        weight_decay=config['training']['optimizer'].get('weight_decay', 0.01)
    )
    
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=config['training']['scheduler']['T_max'],
        eta_min=config['training']['scheduler'].get('eta_min', 1e-6)
    )
    
    # AMP scaler
    scaler = GradScaler('cuda') if config['training'].get('mixed_precision', True) else None
    
    # Checkpoint directory
    save_dir = Path(config['checkpoint']['save_dir'])
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Training loop
    best_metric = 0
    start_epoch = 0
    
    if args.resume:
        print(f"Resuming from {args.resume}")
        checkpoint = torch.load(args.resume, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        start_epoch = checkpoint.get('epoch', 0)
        best_metric = checkpoint.get('best_metric', 0)
    
    num_epochs = config['training']['epochs']
    val_interval = config['validation'].get('interval', 1)
    
    for epoch in range(start_epoch, num_epochs):
        print(f"\nEpoch {epoch + 1}/{num_epochs}")
        print("-" * 40)
        
        # Train
        train_metrics = train_epoch(model, train_loader, optimizer, scaler, device, config)
        print(f"Train: Loss={train_metrics['loss']:.4f}, BCE={train_metrics['bce']:.4f}, IoU={train_metrics['iou']:.4f}")
        
        # Validate
        if (epoch + 1) % val_interval == 0:
            val_metrics = validate(model, val_loader, device)
            print(f"Val: F={val_metrics['f_measure']:.4f}, S={val_metrics['s_measure']:.4f}, "
                  f"MAE={val_metrics['mae']:.4f}, Conf={val_metrics['confidence']:.4f}")
            
            # Save best model
            metric_to_track = val_metrics.get(config['validation'].get('metric', 'f_measure'), val_metrics['f_measure'])
            
            if metric_to_track > best_metric:
                best_metric = metric_to_track
                best_path = save_dir / 'best_model.pth'
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'best_metric': best_metric,
                    'config': config
                }, best_path)
                print(f"Saved best model (metric={best_metric:.4f})")
        
        # Regular checkpoint
        if (epoch + 1) % config['checkpoint'].get('save_interval', 10) == 0:
            ckpt_path = save_dir / f'checkpoint_epoch_{epoch + 1}.pth'
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_metric': best_metric,
                'config': config
            }, ckpt_path)
            print(f"Saved checkpoint: {ckpt_path}")
        
        scheduler.step()
    
    print("\nTraining complete!")
    print(f"Best metric: {best_metric:.4f}")


if __name__ == '__main__':
    main()
