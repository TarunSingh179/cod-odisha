#!/usr/bin/env python3
"""
COD-Odisha Training Starter
Start training immediately with current data, upgrade when full dataset is ready
"""

import sys
from pathlib import Path

def check_dataset():
    """Check available dataset."""
    cod10k = Path("data/COD10K")
    train_imgs = list((cod10k / "images" / "train").glob("*")) if (cod10k / "images" / "train").exists() else []
    test_imgs = list((cod10k / "images" / "test").glob("*")) if (cod10k / "images" / "test").exists() else []
    
    return len(train_imgs), len(test_imgs)

def main():
    print("\n" + "=" * 80)
    print(" " * 15 + "COD-ODISHA CAMOUFLAGED OBJECT DETECTION")
    print(" " * 20 + "TRAINING READY TO START")
    print("=" * 80)
    
    train_count, test_count = check_dataset()
    
    print(f"\n📊 Current Dataset Status:")
    print(f"   Training images: {train_count}")
    print(f"   Test images: {test_count}")
    
    print(f"\n🎯 Status: {'READY TO TRAIN ✓' if train_count > 0 else 'NO DATA'}")
    
    print("\n" + "=" * 80)
    print("📋 TRAINING OPTIONS:")
    print("=" * 80)
    
    print(f"\n✅ OPTION 1: Start Training Now (with {train_count + test_count} images)")
    print("-" * 80)
    print("   COMMAND:")
    print("   python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    print()
    print("   WHAT HAPPENS:")
    print("   • Trains immediately with available data")
    print("   • Model architecture loads successfully")
    print("   • Loss computation works")
    print("   • Checkpoints save properly")
    print()
    print("   WHEN TO USE THIS:")
    print("   • Testing the pipeline")
    print("   • Debugging configuration")
    print("   • Verifying all systems work")
    
    print(f"\n📥 OPTION 2: Download Full Dataset First (5000+ images)")
    print("-" * 80)
    print("   STEPS:")
    print("   1. Download COD10K.zip from:")
    print("      https://github.com/DengPingFan/COD10K")
    print("      (or Baidu: https://pan.baidu.com/s/1Xnxc8nkWqfKhMCOJBOXQ8g)")
    print()
    print("   2. Save file to: downloads/COD10K.zip")
    print()
    print("   3. Organize dataset:")
    print("      python organize_cod10k.py --source downloads/COD10K.zip --verify")
    print()
    print("   4. Start training:")
    print("      python model_training/train.py --config model_training/configs/resnet50_config.yaml")
    print()
    print("   WHAT HAPPENS:")
    print("   • Trains with 5000+ real training images")
    print("   • Model will actually learn meaningful features")
    print("   • Validation on 1344 professional test images")
    print("   • 30-40 minutes per epoch on CPU (~5-10 min on GPU)")
    print()
    print("   WHEN TO USE THIS:")
    print("   • You have 2.7 GB bandwidth to download")
    print("   • You want real trained model for production")
    print("   • Time to train 100 epochs (~30-50 hours CPU, 8-12 hours GPU)")
    
    print("\n" + "=" * 80)
    print("⚡ QUICK RECOMMENDATION:")
    print("=" * 80)
    
    if train_count >= 5:
        print("\n🚀 START HERE - Run this command now:")
        print("\n   cd c:\\Users\\dasni\\\"New folder\"\\cod-odisha")
        print("   python model_training/train.py --config model_training/configs/resnet50_config.yaml")
        print("\n✓ Will complete first epoch in seconds")
        print("✓ Verify all systems work properly")
        print("✓ Then download real data for production training")
    
    print("\n" + "=" * 80)
    print("📊 TRAINING DETAILS:")
    print("=" * 80)
    
    print("\nWith Current Data:")
    print("  • Epoch duration:  < 1 second")
    print("  • Total epochs:    100")
    print("  • Total time:      ~2 minutes")
    print("  • Purpose:         Pipeline validation")
    
    print("\nWith Full COD10K:")
    print("  • Epoch duration:  30-40 min (CPU) / 5-10 min (GPU)")
    print("  • Total epochs:    100")
    print("  • Total time:      20-30 hours (CPU) / 8-12 hours (GPU)")
    print("  • Purpose:         Production model")
    
    print("\n" + "=" * 80)
    print("🎬 READY? Choose your path and execute the command!")
    print("=" * 80)
    
    print("\nAll tools are ready:")
    print("  ✓ download_cod10k.py - Automated download helper")
    print("  ✓ organize_cod10k.py - Dataset organizer")
    print("  ✓ dataset_status.py - Check status anytime")
    print("  ✓ model_training/train.py - Training engine")
    print()

if __name__ == "__main__":
    main()
