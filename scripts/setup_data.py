#!/usr/bin/env python3
"""
COD-Odisha Dataset Setup
=========================
Extracts the COD10K dataset from downloads/archive.zip into the proper
data/COD10K/ directory structure for training.

Usage:
    python setup_data.py
    python setup_data.py --source downloads/archive.zip --verify
"""

import os
import sys
import zipfile
import shutil
import argparse
from pathlib import Path
from collections import defaultdict


def find_archive():
    """Find the dataset archive file."""
    candidates = [
        Path('downloads/archive.zip'),
        Path('downloads/COD10K.zip'),
        Path('downloads/cod10k.zip'),
    ]
    
    for c in candidates:
        if c.exists():
            size_gb = c.stat().st_size / (1024**3)
            print(f"  Found: {c} ({size_gb:.1f} GB)")
            return c
    
    # Search downloads directory for any zip
    downloads = Path('downloads')
    if downloads.exists():
        for f in downloads.glob('*.zip'):
            size_gb = f.stat().st_size / (1024**3)
            if size_gb > 0.5:  # Only consider zips > 500MB
                print(f"  Found: {f} ({size_gb:.1f} GB)")
                return f
    
    return None


def extract_archive(archive_path, extract_to):
    """Extract archive with progress reporting."""
    archive_path = Path(archive_path)
    extract_to = Path(extract_to)
    
    print(f"\n📦 Extracting {archive_path.name}...")
    
    extract_to.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(str(archive_path), 'r') as zf:
        members = zf.namelist()
        total = len(members)
        print(f"  Total files in archive: {total}")
        
        # Count image files
        image_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
        image_count = sum(1 for m in members if Path(m).suffix.lower() in image_exts)
        print(f"  Image files: {image_count}")
        
        # Extract
        for i, member in enumerate(members):
            zf.extract(member, str(extract_to))
            if (i + 1) % 500 == 0 or i == total - 1:
                pct = (i + 1) / total * 100
                print(f"  Extracting: {i+1}/{total} ({pct:.0f}%)")
    
    print(f"  ✅ Extraction complete!")
    return extract_to


def analyze_structure(extract_dir):
    """Analyze extracted directory structure to find images and masks."""
    extract_dir = Path(extract_dir)
    
    print(f"\n🔍 Analyzing directory structure...")
    
    image_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    # Collect all directories that contain images
    image_dirs = defaultdict(int)
    for f in extract_dir.rglob('*'):
        if f.is_file() and f.suffix.lower() in image_exts:
            image_dirs[f.parent] += 1
    
    print(f"  Found {len(image_dirs)} directories with images:")
    for d, count in sorted(image_dirs.items(), key=lambda x: -x[1]):
        rel = d.relative_to(extract_dir)
        print(f"    {rel}: {count} files")
    
    return image_dirs


def organize_dataset(extract_dir, target_dir):
    """
    Organize extracted files into standard COD10K structure:
        target_dir/
            images/train/
            images/test/
            gts/train/
            gts/test/
    """
    extract_dir = Path(extract_dir)
    target_dir = Path(target_dir)
    
    print(f"\n📂 Organizing dataset into {target_dir}...")
    
    for split in ['train', 'test']:
        (target_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (target_dir / 'gts' / split).mkdir(parents=True, exist_ok=True)
    
    image_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    # Strategy: Look for known patterns in directory names
    mappings = {
        # Pattern → (type, split)
        'train_image': ('images', 'train'),
        'training_image': ('images', 'train'),
        'trainimage': ('images', 'train'),
        'test_image': ('images', 'test'),
        'testing_image': ('images', 'test'),
        'testimage': ('images', 'test'),
        'train_gt': ('gts', 'train'),
        'training_gt': ('gts', 'train'),
        'traingt': ('gts', 'train'),
        'train_mask': ('gts', 'train'),
        'training_mask': ('gts', 'train'),
        'test_gt': ('gts', 'test'),
        'testing_gt': ('gts', 'test'),
        'testgt': ('gts', 'test'),
        'test_mask': ('gts', 'test'),
        'testing_mask': ('gts', 'test'),
    }
    
    copied = defaultdict(int)
    
    # Walk through all directories
    for dirpath in extract_dir.rglob('*'):
        if not dirpath.is_dir():
            continue
        
        dir_name = dirpath.name.lower().replace(' ', '_').replace('-', '_')
        parent_name = dirpath.parent.name.lower().replace(' ', '_').replace('-', '_') if dirpath.parent != extract_dir else ''
        
        # Combine dir + parent for matching
        combined = f"{parent_name}_{dir_name}" if parent_name else dir_name
        
        target_type = None
        target_split = None
        
        # Try exact match patterns
        for pattern, (dtype, dsplit) in mappings.items():
            if pattern in combined or pattern in dir_name:
                target_type = dtype
                target_split = dsplit
                break
        
        # Try heuristic matching
        if target_type is None:
            is_train = 'train' in combined
            is_test = 'test' in combined
            is_image = 'image' in combined or 'img' in combined
            is_mask = 'gt' in combined or 'mask' in combined or 'ground' in combined
            
            if is_train and is_image:
                target_type, target_split = 'images', 'train'
            elif is_test and is_image:
                target_type, target_split = 'images', 'test'
            elif is_train and is_mask:
                target_type, target_split = 'gts', 'train'
            elif is_test and is_mask:
                target_type, target_split = 'gts', 'test'
        
        # Copy files if we found a match
        if target_type and target_split:
            dst = target_dir / target_type / target_split
            for f in dirpath.glob('*'):
                if f.is_file() and f.suffix.lower() in image_exts:
                    shutil.copy2(str(f), str(dst / f.name))
                    copied[f"{target_type}/{target_split}"] += 1
    
    # If no files were organized by pattern, try structure-based approach
    if sum(copied.values()) == 0:
        print("  ⚠️  No standard patterns found. Trying structure-based approach...")
        
        # Look for any directory with images and try to classify
        for dirpath in extract_dir.rglob('*'):
            if not dirpath.is_dir():
                continue
            
            files = list(f for f in dirpath.glob('*') if f.is_file() and f.suffix.lower() in image_exts)
            if not files:
                continue
            
            # Check if images are RGB (photos) or grayscale (masks)
            from PIL import Image
            sample = Image.open(str(files[0]))
            is_mask = sample.mode == 'L' or (sample.mode == 'RGB' and len(set(sample.getdata())) < 50)
            
            dtype = 'gts' if is_mask else 'images'
            
            # Use file count heuristic for train/test split
            # Usually train has more files than test
            # Default to train, will sort later
            dsplit = 'train'
            
            dst = target_dir / dtype / dsplit
            for f in files:
                shutil.copy2(str(f), str(dst / f.name))
                copied[f"{dtype}/{dsplit}"] += 1
    
    # Report results
    print("\n📊 Dataset Organization Results:")
    for key, count in sorted(copied.items()):
        print(f"  {key}: {count} files")
    
    return copied


def verify_dataset(target_dir):
    """Verify dataset integrity."""
    target_dir = Path(target_dir)
    
    print(f"\n🔍 Verifying dataset at {target_dir}...")
    
    stats = {}
    all_good = True
    
    for split in ['train', 'test']:
        img_dir = target_dir / 'images' / split
        gt_dir = target_dir / 'gts' / split
        
        images = set(f.stem for f in img_dir.glob('*') if f.is_file()) if img_dir.exists() else set()
        masks = set(f.stem for f in gt_dir.glob('*') if f.is_file()) if gt_dir.exists() else set()
        
        paired = images & masks
        unmatched_images = images - masks
        unmatched_masks = masks - images
        
        stats[split] = {
            'images': len(images),
            'masks': len(masks),
            'paired': len(paired),
            'unmatched_images': len(unmatched_images),
            'unmatched_masks': len(unmatched_masks),
        }
        
        print(f"\n  [{split.upper()}]")
        print(f"    Images:             {len(images)}")
        print(f"    Ground truth masks: {len(masks)}")
        print(f"    Matched pairs:      {len(paired)}")
        
        if unmatched_images:
            print(f"    ⚠️  Images without masks: {len(unmatched_images)}")
            all_good = False
        if unmatched_masks:
            print(f"    ⚠️  Masks without images: {len(unmatched_masks)}")
    
    if all_good and stats.get('train', {}).get('paired', 0) > 0:
        print(f"\n  ✅ Dataset is ready for training!")
    elif stats.get('train', {}).get('paired', 0) > 0:
        print(f"\n  ⚠️  Dataset has some issues but {stats['train']['paired']} paired samples can be used")
    else:
        print(f"\n  ❌ No valid training pairs found!")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='Setup COD-Odisha dataset')
    parser.add_argument('--source', type=str, default=None, help='Path to archive zip file')
    parser.add_argument('--target', type=str, default='data/COD10K', help='Target dataset directory')
    parser.add_argument('--verify', action='store_true', help='Verify dataset after setup')
    parser.add_argument('--verify-only', action='store_true', help='Only verify existing dataset')
    args = parser.parse_args()
    
    print("=" * 60)
    print("  🦎 COD-Odisha Dataset Setup")
    print("=" * 60)
    
    target = Path(args.target)
    
    # Verify only mode
    if args.verify_only:
        verify_dataset(target)
        return
    
    # Find archive
    archive = Path(args.source) if args.source else find_archive()
    
    if archive is None or not archive.exists():
        print("\n  ❌ No archive found!")
        print("  Expected: downloads/archive.zip")
        print("\n  To download the COD10K dataset:")
        print("  1. Go to https://www.kaggle.com/datasets and search for 'COD10K'")
        print("  2. Download the dataset")
        print("  3. Place the zip file in the 'downloads/' directory")
        print("  4. Run this script again")
        sys.exit(1)
    
    # Extract
    temp_dir = Path('temp_dataset_extract')
    if temp_dir.exists():
        shutil.rmtree(str(temp_dir))
    
    extract_archive(archive, temp_dir)
    
    # Analyze
    analyze_structure(temp_dir)
    
    # Organize
    organize_dataset(temp_dir, target)
    
    # Cleanup temp
    print(f"\n🧹 Cleaning up temporary files...")
    shutil.rmtree(str(temp_dir), ignore_errors=True)
    
    # Verify
    if args.verify:
        verify_dataset(target)
    else:
        # Quick check
        for split in ['train', 'test']:
            img_count = len(list((target / 'images' / split).glob('*'))) if (target / 'images' / split).exists() else 0
            print(f"  {split}: {img_count} images")
    
    print("\n✅ Dataset setup complete!")
    print(f"   Location: {target.absolute()}")
    print(f"\n   Next steps:")
    print(f"   • Local training:  python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    print(f"   • Cloud training:  See cloud_training/README.md")


if __name__ == '__main__':
    main()
