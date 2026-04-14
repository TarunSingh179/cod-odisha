#!/usr/bin/env python3
"""
COD10K Dataset Downloader

Downloads the full COD10K (Camouflaged Object Detection) dataset 
and organizes it into the proper directory structure.

Dataset Information:
- Source: https://github.com/DengPingFan/COD10K
- Size: ~2.7 GB (compressed), ~5-6 GB (extracted)
- Classes: 1344 test images + 5000 training images
"""

import os
import sys
import shutil
import zipfile
import urllib.request
from pathlib import Path
from tqdm import tqdm

# Dataset URLs (multiple sources for reliability)
DATASET_URLS = {
    "official": "https://github.com/DengPingFan/COD10K/releases/download/v1.0/COD10K.zip",
    "mirror1": "https://drive.google.com/uc?id=1D9bf1ItunvBy73ZqM3D6p4P4v8nweKOv&export=download",
}

def download_file(url, destination, description=""):
    """Download a file with progress bar."""
    print(f"\n📥 Downloading {description}...")
    print(f"   URL: {url}")
    
    try:
        import urllib.request
        
        # Simple download with progress
        def reporthook(blocknum, blocksize, totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = readsofar * 1e2 / totalsize
                s = f"\r   {readsofar}/{totalsize} bytes ({percent:.1f}%)"
                print(s, end="", flush=True)
        
        urllib.request.urlretrieve(url, destination, reporthook)
        print(f"\n✓ Download complete: {destination}")
        return True
    except Exception as e:
        print(f"\n✗ Download failed: {str(e)}")
        return False


def extract_zip(zip_path, extract_to):
    """Extract ZIP file with progress."""
    print(f"\n📦 Extracting {zip_path}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            total_files = len(zip_ref.namelist())
            for i, file in enumerate(zip_ref.namelist(), 1):
                zip_ref.extract(file, extract_to)
                if i % 100 == 0:
                    print(f"   Extracted {i}/{total_files} files...")
        
        print(f"✓ Extraction complete")
        return True
    except Exception as e:
        print(f"✗ Extraction failed: {str(e)}")
        return False


def organize_dataset(source_dir, target_cod10k_dir):
    """
    Organize extracted dataset into proper structure.
    
    Expected source structure:
    COD10K/
    ├── COD10K_images/
    │   ├── Test/
    │   └── Train/
    ├── Ground_truth/
    │   ├── test/
    │   └── train/
    
    Target structure:
    data/COD10K/
    ├── images/
    │   ├── test/
    │   └── train/
    └── gts/
        ├── test/
        └── train/
    """
    print(f"\n🔧 Organizing dataset...")
    
    source_path = Path(source_dir)
    target_path = Path(target_cod10k_dir)
    
    # Clear existing dummy data
    print("   Clearing existing dummy data...")
    for split in ['train', 'test']:
        for dtype in ['images', 'gts']:
            split_dir = target_path / dtype / split
            if split_dir.exists():
                shutil.rmtree(split_dir)
            split_dir.mkdir(parents=True, exist_ok=True)
    
    # Find source directories (handle various naming conventions)
    possible_image_dirs = [
        source_path / 'COD10K_images',
        source_path / 'COD10K' / 'COD10K_images',
        source_path / 'images',
    ]
    
    possible_gt_dirs = [
        source_path / 'Ground_truth',
        source_path / 'COD10K' / 'Ground_truth',
        source_path / 'gts',
    ]
    
    image_dir = None
    gt_dir = None
    
    for d in possible_image_dirs:
        if d.exists():
            image_dir = d
            break
    
    for d in possible_gt_dirs:
        if d.exists():
            gt_dir = d
            break
    
    if not image_dir or not gt_dir:
        print(f"✗ Could not find source images or ground truth directories")
        print(f"   Looking for: {possible_image_dirs}")
        print(f"   Looking for: {possible_gt_dirs}")
        return False
    
    # Copy training images
    print("   Copying training images...")
    train_src = None
    for possible in [image_dir / 'Train', image_dir / 'train', image_dir / 'TRAIN']:
        if possible.exists():
            train_src = possible
            break
    
    if train_src:
        for img_file in train_src.glob('*'):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                shutil.copy2(img_file, target_path / 'images' / 'train' / img_file.name)
    
    # Copy test images
    print("   Copying test images...")
    test_src = None
    for possible in [image_dir / 'Test', image_dir / 'test', image_dir / 'TEST']:
        if possible.exists():
            test_src = possible
            break
    
    if test_src:
        for img_file in test_src.glob('*'):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                shutil.copy2(img_file, target_path / 'images' / 'test' / img_file.name)
    
    # Copy training ground truth
    print("   Copying training ground truth...")
    train_gt_src = None
    for possible in [gt_dir / 'train', gt_dir / 'Train', gt_dir / 'TRAIN']:
        if possible.exists():
            train_gt_src = possible
            break
    
    if train_gt_src:
        for gt_file in train_gt_src.glob('*'):
            if gt_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                shutil.copy2(gt_file, target_path / 'gts' / 'train' / gt_file.name)
    
    # Copy test ground truth
    print("   Copying test ground truth...")
    test_gt_src = None
    for possible in [gt_dir / 'test', gt_dir / 'Test', gt_dir / 'TEST']:
        if possible.exists():
            test_gt_src = possible
            break
    
    if test_gt_src:
        for gt_file in test_gt_src.glob('*'):
            if gt_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                shutil.copy2(gt_file, target_path / 'gts' / 'test' / gt_file.name)
    
    return True


def verify_dataset(cod10k_dir):
    """Verify dataset integrity."""
    print(f"\n✓ Verifying dataset...")
    
    cod10k_path = Path(cod10k_dir)
    
    stats = {
        'train_images': len(list((cod10k_path / 'images' / 'train').glob('*'))),
        'test_images': len(list((cod10k_path / 'images' / 'test').glob('*'))),
        'train_masks': len(list((cod10k_path / 'gts' / 'train').glob('*'))),
        'test_masks': len(list((cod10k_path / 'gts' / 'test').glob('*'))),
    }
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Training images:   {stats['train_images']:,}")
    print(f"   Test images:       {stats['test_images']:,}")
    print(f"   Training masks:    {stats['train_masks']:,}")
    print(f"   Test masks:        {stats['test_masks']:,}")
    
    # Check if counts match
    if stats['train_images'] == stats['train_masks'] and stats['test_images'] == stats['test_masks']:
        print(f"\n✓ Dataset is properly aligned!")
        return True
    else:
        print(f"\n⚠ Warning: Image/mask counts don't match. Please verify manually.")
        return False


def main():
    print("=" * 70)
    print("COD10K Dataset Downloader")
    print("=" * 70)
    
    # Set up paths
    project_root = Path(__file__).parent
    cod10k_dir = project_root / 'data' / 'COD10K'
    download_dir = project_root / 'downloads'
    temp_extract_dir = project_root / 'temp_extract'
    
    # Create download directory
    download_dir.mkdir(exist_ok=True)
    temp_extract_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Paths:")
    print(f"   Project root: {project_root}")
    print(f"   Dataset dir:  {cod10k_dir}")
    print(f"   Download dir: {download_dir}")
    
    # Attempt download from official source
    zip_path = download_dir / 'COD10K.zip'
    
    if zip_path.exists():
        print(f"\n✓ Found existing download: {zip_path}")
        use_existing = input("Use existing file? (y/n): ").strip().lower()
        if use_existing != 'y':
            zip_path.unlink()
    else:
        # Download dataset
        success = download_file(
            DATASET_URLS["official"],
            str(zip_path),
            "COD10K Dataset (2.7 GB)"
        )
        
        if not success:
            print("\n⚠ Official download failed, trying mirror...")
            success = download_file(
                DATASET_URLS["mirror1"],
                str(zip_path),
                "COD10K Dataset from mirror"
            )
        
        if not success:
            print("\n✗ Could not download dataset from any source")
            print("\nAlternative: Download manually from:")
            print("  https://github.com/DengPingFan/COD10K")
            print(f"  Extract to: {project_root}")
            sys.exit(1)
    
    # Extract dataset
    if not extract_zip(str(zip_path), str(temp_extract_dir)):
        sys.exit(1)
    
    # Organize dataset
    if not organize_dataset(str(temp_extract_dir), str(cod10k_dir)):
        sys.exit(1)
    
    # Verify dataset
    verify_dataset(str(cod10k_dir))
    
    # Cleanup
    print(f"\n🧹 Cleaning up temporary files...")
    shutil.rmtree(temp_extract_dir, ignore_errors=True)
    print(f"✓ Cleanup complete")
    
    print("\n" + "=" * 70)
    print("✅ Dataset Download Complete!")
    print("=" * 70)
    print(f"\nDataset is ready at: {cod10k_dir}")
    print("\nYou can now start training:")
    print(f"  cd {project_root}")
    print(f"  python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    print("=" * 70)


if __name__ == "__main__":
    main()
