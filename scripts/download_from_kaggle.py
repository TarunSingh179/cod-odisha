#!/usr/bin/env python3
r"""
COD10K Dataset Downloader from Kaggle

Requirements:
1. Kaggle account (free): https://www.kaggle.com
2. Kaggle API credentials set up
3. Accept COD10K dataset terms on Kaggle

Setup instructions:
1. Create Kaggle account: https://www.kaggle.com/signup
2. Go to: https://www.kaggle.com/settings/account
3. Click "Create New API Token" - downloads kaggle.json
4. Place kaggle.json in home directory as .kaggle/kaggle.json
5. Run this script
"""

import os
import sys
from pathlib import Path
import subprocess

def check_kaggle_installed():
    """Check if kaggle-api is installed."""
    try:
        import kaggle
        return True
    except ImportError:
        return False

def install_kaggle():
    """Install kaggle-api package."""
    print("\n📦 Installing kaggle-api...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "-q"])
        print("✓ kaggle-api installed")
        return True
    except Exception as e:
        print(f"✗ Failed to install: {e}")
        return False

def check_kaggle_credentials():
    """Check if Kaggle credentials are set up."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    
    if kaggle_json.exists():
        print(f"✓ Found Kaggle credentials at {kaggle_json}")
        return True
    else:
        print(f"✗ Kaggle credentials not found at {kaggle_json}")
        return False

def setup_kaggle_instructions():
    """Show instructions for setting up Kaggle API."""
    kaggle_dir = Path.home() / ".kaggle" / "kaggle.json"
    
    print("\n" + "=" * 80)
    print("🔐 KAGGLE API SETUP REQUIRED")
    print("=" * 80)
    
    print("\nFollow these steps to set up Kaggle API:")
    print("\n1️⃣  Create Kaggle Account (if you don't have one):")
    print("   Visit: https://www.kaggle.com/signup")
    print()
    
    print("2️⃣  Get API Token:")
    print("   Go to: https://www.kaggle.com/settings/account")
    print("   Click: 'Create New API Token'")
    print("   This downloads: kaggle.json")
    print()
    
    print("3️⃣  Place Credentials File:")
    print(f"   Create folder: {Path.home() / '.kaggle'}")
    print(f"   Move kaggle.json to: {kaggle_dir}")
    print()
    
    print("4️⃣  Accept Dataset Terms:")
    print("   Visit: https://www.kaggle.com/datasets/patrickberrill/camouflaged-object-detection")
    print("   Click 'Join' to accept terms")
    print()
    
    print("5️⃣  Run this script again")
    print()

def download_from_kaggle():
    """Download COD10K from Kaggle."""
    try:
        import kaggle
        
        print("\n📥 Downloading COD10K from Kaggle...")
        print("   Dataset: patrickberrill/camouflaged-object-detection")
        
        # Create downloads directory
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)
        
        # Download dataset
        kaggle.api.dataset_download_files(
            'patrickberrill/camouflaged-object-detection',
            path=str(downloads_dir),
            unzip=True
        )
        
        print("✓ Download complete!")
        return True
        
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False

def organize_kaggle_dataset():
    """Organize downloaded Kaggle dataset."""
    import shutil
    import zipfile
    
    print("\n🔧 Organizing dataset...")
    
    downloads_dir = Path("downloads")
    cod10k_path = Path("data/COD10K")
    
    # Create target directories
    for split in ['train', 'test']:
        for dtype in ['images', 'gts']:
            (cod10k_path / dtype / split).mkdir(parents=True, exist_ok=True)
    
    # Find and copy files (flexible for various Kaggle formats)
    image_extensions = ['.jpg', '.jpeg', '.png']
    mask_extensions = ['.png', '.jpg']
    
    file_count = 0
    
    for root, dirs, files in os.walk(downloads_dir):
        for file in files:
            src_path = Path(root) / file
            
            # Try to determine if image or mask and split
            is_image = any(file.lower().endswith(ext) for ext in image_extensions)
            is_mask = any(file.lower().endswith(ext) for ext in mask_extensions)
            
            if not (is_image or is_mask):
                continue
            
            # Determine split (train/test)
            rel_path = str(src_path.relative_to(downloads_dir)).lower()
            is_train = 'train' in rel_path
            is_test = 'test' in rel_path or 'val' in rel_path
            
            # Fallback: use first 80% for train, rest for test
            if not (is_train or is_test):
                if hash(file) % 10 < 8:
                    is_train = True
                else:
                    is_test = True
            
            # Determine if image or mask by content or name
            is_gt = 'gt' in file.lower() or 'mask' in file.lower() or 'annotation' in file.lower()
            
            try:
                if is_image and not is_gt:
                    target_split = 'train' if is_train else 'test'
                    target = cod10k_path / 'images' / target_split / file
                    shutil.copy2(src_path, target)
                    file_count += 1
                    
                elif is_gt or is_mask:
                    target_split = 'train' if is_train else 'test'
                    target = cod10k_path / 'gts' / target_split / file
                    shutil.copy2(src_path, target)
                    file_count += 1
                    
            except Exception as e:
                print(f"⚠ Could not copy {file}: {e}")
    
    print(f"✓ Organized {file_count} files")
    return file_count > 0

def verify_dataset():
    """Verify organized dataset."""
    cod10k_path = Path("data/COD10K")
    
    train_imgs = len(list((cod10k_path / "images" / "train").glob("*")))
    test_imgs = len(list((cod10k_path / "images" / "test").glob("*")))
    train_masks = len(list((cod10k_path / "gts" / "train").glob("*")))
    test_masks = len(list((cod10k_path / "gts" / "test").glob("*")))
    
    print(f"\n✓ Dataset Verification:")
    print(f"  Training images: {train_imgs}")
    print(f"  Test images: {test_imgs}")
    print(f"  Training masks: {train_masks}")
    print(f"  Test masks: {test_masks}")
    
    if train_imgs > 0 and test_imgs > 0:
        print(f"\n✓ Dataset ready for training!")
        return True
    else:
        print(f"\n⚠ Dataset may be incomplete")
        return False

def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "COD10K KAGGLE DATASET DOWNLOADER")
    print("=" * 80)
    
    # Step 1: Check/Install kaggle-api
    if not check_kaggle_installed():
        print("\n📦 kaggle-api not installed")
        if not install_kaggle():
            print("Please install manually: pip install kaggle")
            sys.exit(1)
    
    # Step 2: Check credentials
    if not check_kaggle_credentials():
        setup_kaggle_instructions()
        sys.exit(1)
    
    # Step 3: Download
    if not download_from_kaggle():
        print("\n⚠ Download may have failed or dataset not available")
        print("Try alternative sources:")
        print("  GitHub: https://github.com/DengPingFan/COD10K")
        print("  Baidu: https://pan.baidu.com/s/1Xnxc8nkWqfKhMCOJBOXQ8g")
        sys.exit(1)
    
    # Step 4: Organize
    if not organize_kaggle_dataset():
        print("\n✗ Failed to organize dataset")
        sys.exit(1)
    
    # Step 5: Verify
    if verify_dataset():
        print("\n" + "=" * 80)
        print("✅ DATASET READY FOR TRAINING!")
        print("=" * 80)
        print("\nStart training with:")
        print("  python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    
if __name__ == "__main__":
    main()
