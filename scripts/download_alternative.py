#!/usr/bin/env python3
"""
COD10K Dataset - Alternative Download via requests library
Uses requests + tqdm for reliable downloads
"""

import os
from pathlib import Path

def try_requests_download():
    """Try downloading with requests library."""
    try:
        import requests
        from tqdm import tqdm
        
        print("\n📥 Using requests library for download...")
        
        urls = [
            "https://github.com/DengPingFan/COD10K/archive/refs/heads/main.zip",
            "https://codeload.github.com/DengPingFan/COD10K/zip/main",
        ]
        
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)
        
        for url in urls:
            try:
                print(f"\n  Trying: {url}")
                response = requests.get(url, stream=True, timeout=30)
                
                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    zip_path = downloads_dir / "COD10K_repo.zip"
                    
                    with open(zip_path, 'wb') as f:
                        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    
                    print(f"\n✓ Downloaded to {zip_path}")
                    return str(zip_path)
            except Exception as e:
                print(f"  ✗ Failed: {str(e)[:100]}")
                continue
        
        return None
    
    except ImportError:
        print("⚠ requests library not installed")
        return None

def try_urllib_resumable():
    """Try urllib with basic resumable download."""
    import urllib.request
    import shutil
    from pathlib import Path
    
    print("\n📥 Using urllib for download...")
    
    url = "https://github.com/DengPingFan/COD10K/archive/refs/heads/main.zip"
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    zip_path = downloads_dir / "COD10K_repo.zip"
    
    try:
        print(f"  Downloading from: {url}")
        print(f"  Saving to: {zip_path}")
        
        def reporthook(blocknum, blocksize, totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = min(100, readsofar * 100 / totalsize)
                print(f"\r  Progress: {percent:.1f}% ({readsofar}/{totalsize} bytes)", end="", flush=True)
        
        urllib.request.urlretrieve(url, str(zip_path), reporthook)
        print(f"\n✓ Downloaded successfully!")
        return str(zip_path)
    
    except Exception as e:
        print(f"\n✗ Download failed: {str(e)}")
        return None

def extract_and_organize(zip_path):
    """Extract and organize the downloaded file."""
    import zipfile
    import shutil
    
    print(f"\n📦 Processing {zip_path}...")
    
    try:
        zip_path = Path(zip_path)
        extract_dir = zip_path.parent / "extracted"
        
        print("  Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print("  Organizing...")
        
        # The extracted repo has images in specific structure
        repo_root = extract_dir / "COD10K-main"
        
        # Create target directories
        cod10k_path = Path("data/COD10K")
        for split in ['train', 'test']:
            for dtype in ['images', 'gts']:
                (cod10k_path / dtype / split).mkdir(parents=True, exist_ok=True)
        
        # Copy from extracted location
        if repo_root.exists():
            src_imgs = repo_root / "Imgs"
            src_gts = repo_root / "GT"
            
            if src_imgs.exists() and src_gts.exists():
                print(f"  Found images and GT in repo")
                
                # Copy to data/COD10K
                for item in src_imgs.rglob("*"):
                    if item.is_file() and item.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        rel = item.relative_to(src_imgs)
                        target = cod10k_path / "images" / str(rel)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target)
                
                # Copy GT
                for item in src_gts.rglob("*"):
                    if item.is_file() and item.suffix.lower() in ['.png', '.jpg']:
                        rel = item.relative_to(src_gts)
                        target = cod10k_path / "gts" / str(rel)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target)
        
        # Cleanup
        shutil.rmtree(extract_dir, ignore_errors=True)
        
        print("✓ Organization complete!")
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("COD10K Dataset Download - Alternative Method")
    print("=" * 70)
    
    # Try requests first
    zip_path = try_requests_download()
    
    # Fallback to urllib
    if not zip_path:
        print("\nFalling back to urllib method...")
        zip_path = try_urllib_resumable()
    
    if zip_path:
        if extract_and_organize(zip_path):
            print("\n✓ Dataset download and organization complete!")
            print("\nYou can now start training:")
            print("  python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    else:
        print("\n✗ Could not complete automatic download")
        print("\nManual option:")
        print("  1. Visit: https://github.com/DengPingFan/COD10K")
        print("  2. Click Code → Download ZIP")
        print("  3. Save to: downloads/COD10K.zip")
        print("  4. Run: python organize_cod10k.py --source downloads/COD10K.zip --verify")

if __name__ == "__main__":
    main()
