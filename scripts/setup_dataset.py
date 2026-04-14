#!/usr/bin/env python3
"""
COD10K Easy Setup - Choose Your Download Method
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 70)
    print("COD10K Dataset Setup")
    print("=" * 70)
    
    print("\n⚠ Automated download URLs are outdated.")
    print("\nChoose your preferred method to get the dataset:\n")
    
    print("📌 OPTION 1: GitHub Releases (Recommended)")
    print("-" * 70)
    print("1. Go to: https://github.com/DengPingFan/COD10K")
    print("2. Click 'Releases' tab")
    print("3. Download 'COD10K.zip' from latest release")
    print("4. Save to: downloads/COD10K.zip")
    print("5. Run: python organize_cod10k.py --source downloads/COD10K.zip --verify")
    print()
    
    print("📌 OPTION 2: Direct GitHub Link")
    print("-" * 70)
    print("Download (Windows Command):")
    print('  powershell -Command "Invoke-WebRequest -Uri https://github.com/DengPingFan/')
    print('COD10K/releases/download/v1.0/COD10K.zip -OutFile downloads/COD10K.zip"')
    print()
    
    print("📌 OPTION 3: Using Google Drive (if available)")
    print("-" * 70)
    print("Search for: 'COD10K dataset google drive'")
    print("Download and extract to: downloads/")
    print()
    
    print("📌 OPTION 4: Alternative - Use Baidu Cloud (Mainland China)")
    print("-" * 70)
    print("Link: https://pan.baidu.com/s/1Xnxc8nkWqfKhMCOJBOXQ8g")
    print("Code: cod4 (typically)")
    print()
    
    print("=" * 70)
    print("After downloading, run:")
    print("  python organize_cod10k.py --source downloads/COD10K.zip --verify")
    print("Then training will start immediately with real data!")
    print("=" * 70)
    
    # Check if file already exists
    cod10k_zip = Path("downloads/COD10K.zip")
    if cod10k_zip.exists():
        print(f"\n✓ Found existing: {cod10k_zip}")
        print(f"  Size: {cod10k_zip.stat().st_size / 1024 / 1024:.1f} MB")
        print("\nRun: python organize_cod10k.py --source downloads/COD10K.zip --verify")
    else:
        print(f"\n❌ No dataset file found at: {cod10k_zip}")
        print("\nPlease download using one of the methods above.")


if __name__ == "__main__":
    main()
