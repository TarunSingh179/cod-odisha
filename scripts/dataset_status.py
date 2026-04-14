#!/usr/bin/env python3
"""
COD10K Dataset Setup - Complete Guide & Status Check

Automated download URLs are outdated. Use this guide to:
1. Check current dataset status
2. Download manually (with options)
3. Organize when you have the file
4. Start training (with current data)
"""

from pathlib import Path
import os

def check_dataset_status():
    """Check what dataset is currently available."""
    cod10k_path = Path("data/COD10K")
    dummy_imgs = len(list((cod10k_path / "images" / "train").glob("*"))) if (cod10k_path / "images" / "train").exists() else 0
    dummy_test = len(list((cod10k_path / "images" / "test").glob("*"))) if (cod10k_path / "images" / "test").exists() else 0
    
    downloaded_zip = Path("downloads/COD10K.zip")
    
    return {
        "current_train_imgs": dummy_imgs,
        "current_test_imgs": dummy_test,
        "zip_exists": downloaded_zip.exists(),
        "zip_size_mb": downloaded_zip.stat().st_size / 1024 / 1024 if downloaded_zip.exists() else 0
    }

def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "COD10K DATASET SETUP - COMPLETE GUIDE")
    print("=" * 80)
    
    # Status
    status = check_dataset_status()
    
    print("\n📊 CURRENT STATUS:")
    print("-" * 80)
    print(f"  Training images:  {status['current_train_imgs']} (full dataset: 5000+)")
    print(f"  Test images:      {status['current_test_imgs']} (full dataset: 1344+)")
    
    if status['zip_exists']:
        print(f"  Downloaded ZIP:   YES ({status['zip_size_mb']:.1f} MB)")
    else:
        print(f"  Downloaded ZIP:   NO (Need to download)")
    
    print("\n" + "=" * 80)
    print("🚀 WHAT TO DO NOW:")
    print("=" * 80)
    
    if status['zip_exists'] and status['zip_size_mb'] > 100:
        print("\n✓ Dataset ZIP found! Ready to organize:")
        print("  python organize_cod10k.py --source downloads/COD10K.zip --verify")
        print("\n  Then start training with real data:")
        print("  python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    
    elif status['current_train_imgs'] > 10:
        print("\n✓ Dataset already installed! Can start training:")
        print("  python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    
    else:
        print("\n❌ Need to download COD10K dataset first")
        print("\n📥 QUICK DOWNLOAD OPTIONS:\n")
        
        print("  OPTION 1: GitHub Repository (Official Source)")
        print("  " + "-" * 76)
        print("  • Visit: https://github.com/DengPingFan/COD10K")  
        print("  • Click 'Code' → 'Download ZIP' OR find Releases tab")
        print("  • Save as: downloads/COD10K.zip")
        print()
        
        print("  OPTION 2: Baidu Cloud (Mainland China - Fastest)")
        print("  " + "-" * 76)
        print("  • Link: https://pan.baidu.com/s/1Xnxc8nkWqfKhMCOJBOXQ8g")
        print("  • Code: cod4")
        print("  • Save as: downloads/COD10K.zip")
        print()
        
        print("  OPTION 3: Keep Current Dummy Data & Continue")
        print("  " + "-" * 76)
        print("  • Start training with 7 dummy images to verify pipeline")
        print("  • When full dataset ready, replace and retrain")
        print("  • Command: python model_training/train.py --config model_training/configs/resnet50_config.yaml")
        print()
    
    print("\n" + "=" * 80)
    print("📋 AFTER DOWNLOADING:")
    print("=" * 80)
    
    print("\n1️⃣  Place ZIP file:")
    print("   Move COD10K.zip to: downloads/COD10K.zip")
    print()
    
    print("2️⃣  Organize dataset:")
    print("   python organize_cod10k.py --source downloads/COD10K.zip --verify")
    print()
    
    print("3️⃣  Verify organization:")
    print("   python -c \"from pathlib import Path; Path('data/COD10K').__str__()\"")
    print()
    
    print("4️⃣  Start training:")
    print("   python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    print()
    print("5️⃣  Monitor progress:")
    print("   Watch loss decrease, validate metrics per epoch")
    print()
    
    print("=" * 80)
    print("💡 TRAINING EXPECTATIONS:")
    print("=" * 80)
    
    print("\nWith Dummy Dataset (7 images):")
    print("  • Epoch time:     <1 second")
    print("  • Use case:       Pipeline testing & debugging")
    print("  • Training value: None (won't converge)")
    print()
    
    print("With Full COD10K (6344 images):")
    print("  • Epoch time:     30-40 min (CPU) / 5-10 min (GPU)")
    print("  • Training value: Real model that detects camouflaged objects")
    print("  • Dataset size:   ~6 GB extracted, 2.7 GB compressed")
    print()
    
    print("=" * 80)
    print("✅ YOU CAN START NOW WITH EITHER OPTION:")
    print("=" * 80)
    print("\n  Option A: Train now with dummy data (test pipeline)")
    print("           python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    print()
    print("  Option B: Download full dataset first, then train with real data")
    print("           1. Download COD10K from GitHub/Baidu")
    print("           2. Save to downloads/COD10K.zip")
    print("           3. python organize_cod10k.py --source downloads/COD10K.zip --verify")
    print("           4. python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
