#!/usr/bin/env python3
"""
Search for COD10K dataset on Kaggle
Helps find the correct dataset path/username
"""

import sys

def search_kaggle_datasets():
    """Search for COD datasets on Kaggle."""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        print("\n" + "=" * 80)
        print("SEARCHING FOR COD DATASETS ON KAGGLE")
        print("=" * 80)
        
        # Search for COD-related datasets using command line
        print("\nSearching for 'COD10K' datasets...")
        
        try:
            import subprocess
            result = subprocess.run(
                [
                    "kaggle", "datasets", "list",
                    "-s", "COD10K"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"⚠ Search returned: {result.stderr}")
        
        except Exception as e:
            print(f"Search error: {e}")
        
        print("\n" + "=" * 80)
        print("QUICK SOLUTION: GitHub or Baidu")  
        print("=" * 80)
        print("\n📥 The COD10K official source is on GitHub:")
        print("   https://github.com/DengPingFan/COD10K")
        print("\n   Steps:")
        print("   1. Visit the GitHub link")
        print("   2. Click 'Code' → 'Download ZIP'")
        print("   3. Save to: downloads/COD10K.zip")
        print("   4. Run: python organize_cod10k.py --source downloads/COD10K.zip --verify")
        
        print("\n🇨🇳 For mainland China (faster):")
        print("   Baidu Cloud: https://pan.baidu.com/s/1Xnxc8nkWqfKhMCOJBOXQ8g")
        print("   Code: cod4")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    search_kaggle_datasets()
