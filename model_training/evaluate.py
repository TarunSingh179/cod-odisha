"""
COD-Odisha Evaluation Script

Evaluates trained model on test sets and computes metrics:
- S-measure (Structure measure)
- E-measure (Enhanced alignment measure)
- F-measure (F-beta score)
- MAE (Mean Absolute Error)

Usage:
    python evaluate.py --checkpoint checkpoints/best_model.pth --config configs/resnet50_config.yaml
"""

import argparse
import yaml
from pathlib import Path

import torch
import numpy as np
from torch.utils.data import DataLoader
from tqdm import tqdm

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.models import build_model
from model_training.datasets.odisha_cod_dataset import build_dataset


def compute_f_measure(pred, gt, beta_square=0.3):
    """
    Compute F-measure with specified beta.
    Default beta^2=0.3 as used in COD literature.
    """
    pred_binary = (pred > 0.5).astype(float)
    
    tp = np.sum(pred_binary * gt)
    fp = np.sum(pred_binary * (1 - gt))
    fn = np.sum((1 - pred_binary) * gt)
    
    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    
    f_measure = (1 + beta_square) * precision * recall / (beta_square * precision + recall + 1e-8)
    
    return f_measure, precision, recall


def compute_mae(pred, gt):
    """Mean Absolute Error."""
    return np.mean(np.abs(pred - gt))


def compute_s_measure(pred, gt):
    """
    S-measure (Structure measure).
    Simplified implementation based on region similarity.
    """
    # Structure similarity approximation
    pred_mean = pred.mean()
    gt_mean = gt.mean()
    
    # Covariance
    covariance = np.mean((pred - pred_mean) * (gt - gt_mean))
    pred_var = np.var(pred)
    gt_var = np.var(gt)
    
    # Similar to SSIM structure component
    s_measure = (2 * covariance + 1e-8) / (pred_var + gt_var + 1e-8)
    
    return max(0, s_measure)


def compute_e_measure(pred, gt):
    """
    E-measure (Enhanced alignment measure).
    Simplified implementation.
    """
    # Alignment matrix
    alignment = 1 - np.abs(pred - gt)
    
    # Enhanced alignment
    e_measure = np.mean(alignment)
    
    return e_measure


@torch.no_grad()
def evaluate_model(model, dataloader, device):
    """
    Evaluate model on dataset.
    """
    model.eval()
    
    all_metrics = {
        'f_measure': [],
        'precision': [],
        'recall': [],
        'mae': [],
        's_measure': [],
        'e_measure': [],
        'confidence': []
    }
    
    for batch in tqdm(dataloader, desc="Evaluating"):
        images = batch['image'].to(device)
        masks = batch['mask'].to(device)
        
        outputs = model(images)
        
        preds = outputs['mask'].cpu().numpy()
        gts = masks.cpu().numpy()
        
        # Process each sample in batch
        for pred, gt in zip(preds, gts):
            pred_flat = pred.flatten()
            gt_flat = gt.flatten()
            
            # Compute metrics
            f_measure, precision, recall = compute_f_measure(pred_flat, gt_flat)
            mae = compute_mae(pred_flat, gt_flat)
            s_measure = compute_s_measure(pred_flat, gt_flat)
            e_measure = compute_e_measure(pred_flat, gt_flat)
            
            all_metrics['f_measure'].append(f_measure)
            all_metrics['precision'].append(precision)
            all_metrics['recall'].append(recall)
            all_metrics['mae'].append(mae)
            all_metrics['s_measure'].append(s_measure)
            all_metrics['e_measure'].append(e_measure)
    
    # Compute mean metrics
    mean_metrics = {k: float(np.mean(v)) for k, v in all_metrics.items()}
    
    return mean_metrics


def main():
    parser = argparse.ArgumentParser(description='Evaluate COD-Odisha model')
    parser.add_argument('--checkpoint', type=str, required=True, help='Path to checkpoint')
    parser.add_argument('--config', type=str, required=True, help='Path to config YAML')
    parser.add_argument('--split', type=str, default='test', help='Dataset split to evaluate')
    parser.add_argument('--save-results', type=str, default=None, help='Save results to file')
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    print("=" * 60)
    print("COD-Odisha Evaluation")
    print("=" * 60)
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Config: {args.config}")
    print(f"Split: {args.split}")
    print("=" * 60)
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    
    # Build model
    model = build_model(
        backbone=config['model']['backbone'],
        pretrained=False
    )
    
    # Load checkpoint
    checkpoint = torch.load(args.checkpoint, map_location=device)
    state_dict = checkpoint['model_state_dict']
    
    # Handle DataParallel prefix
    state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}
    model.load_state_dict(state_dict, strict=False)
    
    model = model.to(device)
    model.eval()
    
    print(f"Loaded checkpoint from epoch {checkpoint.get('epoch', 'unknown')}")
    
    # Build dataset
    dataset = build_dataset(config['dataset'], split=args.split)
    dataloader = DataLoader(
        dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False,
        num_workers=config['training'].get('num_workers', 4),
        pin_memory=True
    )
    
    print(f"Dataset: {len(dataset)} samples")
    
    # Evaluate
    metrics = evaluate_model(model, dataloader, device)
    
    # Print results
    print("\n" + "=" * 60)
    print("Evaluation Results")
    print("=" * 60)
    print(f"F-measure (max):   {metrics['f_measure']:.4f}")
    print(f"S-measure:         {metrics['s_measure']:.4f}")
    print(f"E-measure:         {metrics['e_measure']:.4f}")
    print(f"MAE:               {metrics['mae']:.4f}")
    print(f"Precision:         {metrics['precision']:.4f}")
    print(f"Recall:            {metrics['recall']:.4f}")
    print("=" * 60)
    
    # Save results
    if args.save_results:
        import json
        with open(args.save_results, 'w') as f:
            json.dump({k: float(v) for k, v in metrics.items()}, f, indent=2)
        print(f"Results saved to {args.save_results}")


if __name__ == '__main__':
    main()
