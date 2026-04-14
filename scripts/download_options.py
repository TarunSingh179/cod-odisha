#!/usr/bin/env python3
"""
COD10K Dataset - Multiple Download Options

Since official release links may change, this script provides multiple ways to get the dataset.
"""

import os
import sys
from pathlib import Path

DOWNLOAD_OPTIONS = {
    "1": {
        "name": "GitHub Main Repository (Try First)",
        "url": "https://github.com/DengPingFan/COD10K",
        "instructions": [
            "1. Visit: https://github.com/DengPingFan/COD10K",
            "2. Look for 'Releases' or download link on main page",
            "3. Download the COD10K.zip file",
            "4. Save to: downloads/COD10K.zip"
        ]
    },
    "2": {
        "name": "Baidu Cloud (Mainland China - Fast)",
        "url": "https://pan.baidu.com/s/1Xnxc8nkWqfKhMCOJBOXQ8g",
        "instructions": [
            "1. Visit Baidu Cloud link",
            "2. Extraction code: cod4 (or similar)",
            "3. Download COD10K.zip",
            "4. Save to: downloads/COD10K.zip"
        ]
    },
    "3": {
        "name": "Search for 'COD10K dataset' on major platforms",
        "url": "Google Scholar, Papers with Code, etc.",
        "instructions": [
            "1. Search: 'COD10K dataset download'",
            "2. Look for official hosted versions",
            "3. Download the dataset",
            "4. Save to: downloads/COD10K.zip"
        ]
    },
    "4": {
        "name": "Use Smaller Alternative Datasets",
        "url": "NC4K, COCO-COD, SINet, etc.",
        "instructions": [
            "1. These datasets have similar format but smaller size",
            "2. Can get started with training faster",
            "3. Run with small dataset, then upgrade",
            "4. Search: '<dataset_name> download'"
        ]
    }
}

def show_menu():
    print("\n" + "=" * 70)
    print("COD10K Dataset - Download Methods")
    print("=" * 70)
    print("\nThe automated download couldn't reach the release server.")
    print("Please choose a download method and get the dataset:\n")
    
    for option, info in DOWNLOAD_OPTIONS.items():
        print(f"📌 OPTION {option}: {info['name']}")
        print(f"   URL: {info['url']}")
        for instruction in info['instructions']:
            print(f"   {instruction}")
        print()

def check_existing():
    """Check if dataset already exists."""
    cod10k_zip = Path("downloads") / "COD10K.zip"
    
    if cod10k_zip.exists():
        size_mb = cod10k_zip.stat().st_size / 1024 / 1024
        print("=" * 70)
        print(f"✓ Found existing dataset file!")
        print(f"  Path: {cod10k_zip.absolute()}")
        print(f"  Size: {size_mb:.1f} MB")
        print("=" * 70)
        print("\nNext step: Extract and organize")
        print("  python organize_cod10k.py --source downloads/COD10K.zip --verify")
        return True
    
    return False

def main():
    print("\n" + "=" * 70)
    print("COD10K Dataset Setup Helper")
    print("=" * 70)
    
    # Check if dataset already exists
    if check_existing():
        return
    
    # Show download options
    show_menu()
    
    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("\n1. Download COD10K.zip using one of the methods above")
    print("2. Place it in: downloads/COD10K.zip")
    print("3. Run this command to organize:")
    print("   python organize_cod10k.py --source downloads/COD10K.zip --verify")
    print("\n4. Then start training:")
    print("   python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    print("\n" + "=" * 70)
    
    # Provide quick start if user has curl/wget
    print("\n💡 QUICK DOWNLOAD TIPS:")
    print("-" * 70)
    
    print("\nIf you have aria2c (fast multi-threaded downloader):")
    print("  aria2c -x 4 'https://github.com/DengPingFan/COD10K/releases/download/...'")
    
    print("\nIf you have IDM (Internet Download Manager):")
    print("  Copy the GitHub URL and paste into IDM")
    
    print("\nIf you're on WSL or Linux:")
    print("  wget 'https://github.com/DengPingFan/COD10K/releases/download/...'")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
