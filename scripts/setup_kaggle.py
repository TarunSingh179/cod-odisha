#!/usr/bin/env python3
"""
Kaggle Credentials Setup Helper
Run this after downloading kaggle.json from Kaggle
"""

from pathlib import Path
import shutil
import sys

def setup_kaggle():
    """Help user set up Kaggle credentials."""
    print("\n" + "=" * 80)
    print(" " * 20 + "KAGGLE CREDENTIALS SETUP")
    print("=" * 80)
    
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json_dest = kaggle_dir / "kaggle.json"
    
    # Step 1: Check if already set up
    if kaggle_json_dest.exists():
        print(f"\n✓ Kaggle credentials already set up!")
        print(f"  Location: {kaggle_json_dest}")
        print(f"\n  Run: python download_from_kaggle.py")
        return True
    
    # Step 2: Show what to do
    print(f"\n❌ Kaggle credentials not found at:")
    print(f"  {kaggle_json_dest}")
    
    print(f"\n📋 SETUP STEPS:")
    print(f"\n1️⃣  Download kaggle.json from Kaggle:")
    print(f"   • Go to: https://www.kaggle.com/settings/account")
    print(f"   • Click 'Create New API Token'")
    print(f"   • Your browser downloads: kaggle.json")
    
    print(f"\n2️⃣  Place it in the correct location:")
    print(f"   • Create folder: {kaggle_dir}")
    print(f"   • Move kaggle.json to: {kaggle_json_dest}")
    
    # Try to help find downloaded file
    print(f"\n3️⃣  Automated Setup (if you have kaggle.json):")
    downloads_dir = Path.home() / "Downloads"
    possible_files = list(downloads_dir.glob("kaggle.json"))
    
    if possible_files:
        print(f"\n   Found kaggle.json in Downloads!")
        source = possible_files[0]
        print(f"   Source: {source}")
        
        try:
            # Create .kaggle directory
            kaggle_dir.mkdir(exist_ok=True, parents=True)
            
            # Copy file
            shutil.copy2(source, kaggle_json_dest)
            
            print(f"   ✓ Copied to: {kaggle_json_dest}")
            print(f"\n✅ Setup complete!")
            print(f"   Next: python download_from_kaggle.py")
            
            # Also set permissions (Windows doesn't restrict like Linux)
            return True
            
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            return False
    else:
        print(f"\n   ⚠ kaggle.json not found in Downloads folder")
        print(f"   Manual option:")
        print(f"   1. Download from: https://www.kaggle.com/settings/account")
        print(f"   2. Create folder: {kaggle_dir}")
        print(f"   3. Move kaggle.json to: {kaggle_json_dest}")
        print(f"   4. Run: python setup_kaggle.py (again)")
        return False
    
    print(f"\n4️⃣  Then download dataset:")
    print(f"   python download_from_kaggle.py")

def main():
    setup_kaggle()

if __name__ == "__main__":
    main()
