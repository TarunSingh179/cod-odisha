#!/usr/bin/env python3
"""
Direct COD10K Download from GitHub
Uses multiple methods to download the dataset
"""

import os
import sys
from pathlib import Path

def try_direct_github_download():
    """Try downloading directly from GitHub releases."""
    print("\n📥 Attempting direct GitHub download...")
    
    import urllib.request
    import shutil
    
    # GitHub raw content URL for the main repository
    repo_urls = [
        "https://codeload.github.com/DengPingFan/COD10K/zip/main",
        "https://github.com/DengPingFan/COD10K/archive/refs/heads/main.zip",
    ]
    
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    zip_path = downloads_dir / "COD10K_github.zip"
    
    for url in repo_urls:
        try:
            print(f"\n  Trying: {url}")
            
            def reporthook(blocknum, blocksize, totalsize):
                readsofar = blocknum * blocksize
                if totalsize > 0:
                    percent = min(100, readsofar * 100 / totalsize)
                    mb_so_far = readsofar / 1024 / 1024
                    mb_total = totalsize / 1024 / 1024
                    print(f"\r    Progress: {percent:.1f}% ({mb_so_far:.1f}/{mb_total:.1f} MB)", end="", flush=True)
            
            urllib.request.urlretrieve(url, str(zip_path), reporthook)
            print(f"\n✓ Downloaded successfully to {zip_path}")
            return str(zip_path)
            
        except Exception as e:
            print(f"\n  ✗ Failed: {str(e)[:100]}")
            continue
    
    return None

def extract_and_organize(zip_path):
    """Extract and organize the GitHub repository."""
    import zipfile
    import shutil
    
    print(f"\n📦 Processing downloaded file...")
    
    try:
        zip_path = Path(zip_path)
        extract_dir = zip_path.parent / "extracted"
        
        print(f"  Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the extracted folder
        extracted_items = list(extract_dir.glob("*"))
        if extracted_items:
            repo_root = extracted_items[0]
            print(f"  Found repo at: {repo_root.name}")
            
            # Look for image folders
            images_found = False
            for pattern in ["Imgs", "Images", "images", "IMG", "img"]:
                src_path = repo_root / pattern
                if src_path.exists():
                    print(f"  Found images folder: {pattern}")
                    images_found = True
                    break
            
            if images_found:
                print(f"✓ Repository extracted successfully")
                
                # Now organize
                print(f"\n🔧 Organizing into COD10K structure...")
                organize_github_repo(repo_root)
                
                # Cleanup
                shutil.rmtree(extract_dir, ignore_errors=True)
                return True
        
        print("✗ Could not find image folders in extracted repository")
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def organize_github_repo(repo_root):
    """Organize GitHub repository into standard structure."""
    import shutil
    
    repo_root = Path(repo_root)
    cod10k_path = Path("data/COD10K")
    
    # Create target directories
    for split in ['train', 'test']:
        for dtype in ['images', 'gts']:
            (cod10k_path / dtype / split).mkdir(parents=True, exist_ok=True)
    
    # Find and copy files
    extensions_img = ['.jpg', '.jpeg', '.png']
    extensions_mask = ['.png']
    
    file_count = 0
    
    for root, dirs, files in os.walk(repo_root):
        for file in files:
            src = Path(root) / file
            rel_path = str(src.relative_to(repo_root)).lower()
            
            # Determine if image or GT
            is_img = any(file.lower().endswith(ext) for ext in extensions_img)
            is_gt = 'gt' in rel_path or 'ground' in rel_path or 'mask' in rel_path
            
            if not is_img:
                continue
            
            # Determine train/test
            is_train = 'train' in rel_path
            is_test = 'test' in rel_path or 'eval' in rel_path
            
            if not (is_train or is_test):
                continue
            
            try:
                split = 'train' if is_train else 'test'
                
                if is_gt:
                    target = cod10k_path / 'gts' / split / file
                else:
                    target = cod10k_path / 'images' / split / file
                
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
                file_count += 1
                
                if file_count % 100 == 0:
                    print(f"  Copied {file_count} files...")
            
            except Exception as e:
                pass
    
    print(f"✓ Organized {file_count} files")
    return file_count > 0

def verify_dataset():
    """Verify the organized dataset."""
    cod10k = Path("data/COD10K")
    
    train_imgs = len(list((cod10k / "images" / "train").glob("*")))
    test_imgs = len(list((cod10k / "images" / "test").glob("*")))
    train_masks = len(list((cod10k / "gts" / "train").glob("*")))
    test_masks = len(list((cod10k / "gts" / "test").glob("*")))
    
    print(f"\n✓ Dataset Statistics:")
    print(f"  Training images: {train_imgs}")
    print(f"  Test images: {test_imgs}")
    print(f"  Training masks: {train_masks}")
    print(f"  Test masks: {test_masks}")
    
    if train_imgs > 0 or test_imgs > 0:
        print(f"\n✓ Dataset ready for training!")
        return True
    else:
        print(f"\n⚠ Dataset appears empty")
        return False

def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "COD10K DIRECT GITHUB DOWNLOAD")
    print("=" * 80)
    
    # Download
    zip_path = try_direct_github_download()
    
    if not zip_path:
        print("\n✗ Could not download from any GitHub mirror")
        print("\nManual option:")
        print("  1. Visit: https://github.com/DengPingFan/COD10K")
        print("  2. Click 'Code' → 'Download ZIP'")
        print("  3. Save to: downloads/COD10K.zip")
        print("  4. Run: python organize_cod10k.py --source downloads/COD10K.zip --verify")
        sys.exit(1)
    
    # Extract and organize
    if not extract_and_organize(zip_path):
        print("\n✗ Failed to extract and organize")
        sys.exit(1)
    
    # Verify
    if verify_dataset():
        print("\n" + "=" * 80)
        print("✅ DOWNLOAD COMPLETE - READY TO TRAIN!")
        print("=" * 80)
        print("\nStart training:")
        print("  python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    
if __name__ == "__main__":
    main()
