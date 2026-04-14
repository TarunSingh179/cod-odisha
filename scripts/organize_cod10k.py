#!/usr/bin/env python3
"""
COD10K Dataset Organizer

Helps organize downloaded COD10K dataset into proper directory structure.
Can handle various download formats and alternative datasets.
"""

import os
import shutil
from pathlib import Path
import argparse

def find_and_copy_images(source_dir, target_train_dir, target_test_dir):
    """Find and copy images from source directory."""
    source_path = Path(source_dir)
    
    # Look for image directories with various naming conventions
    image_search_patterns = [
        'images', 'Images', 'IMAGES',
        'imgs', 'Imgs', 'IMGS',
        'img', 'Img', 'IMG',
    ]
    
    train_patterns = ['train', 'Train', 'TRAIN', 'Tr', 'training']
    test_patterns = ['test', 'Test', 'TEST', 'Ts', 'testing', 'eval']
    
    train_count = 0
    test_count = 0
    
    print(f"\n🔍 Searching for images in {source_path}...")
    
    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                rel_path = os.path.relpath(root, source_path)
                
                # Determine if this is train or test
                is_train = any(p.lower() in rel_path.lower() for p in train_patterns)
                is_test = any(p.lower() in rel_path.lower() for p in test_patterns)
                
                if is_train:
                    shutil.copy2(os.path.join(root, file), os.path.join(target_train_dir, file))
                    train_count += 1
                    if train_count % 500 == 0:
                        print(f"  Copied {train_count} training images...")
                elif is_test:
                    shutil.copy2(os.path.join(root, file), os.path.join(target_test_dir, file))
                    test_count += 1
                    if test_count % 500 == 0:
                        print(f"  Copied {test_count} test images...")
    
    return train_count, test_count


def organize_manual_download(zip_path, cod10k_dir):
    """Organize manually downloaded and extracted COD10K."""
    print(f"\n📦 Organizing dataset from {zip_path}...")
    
    import zipfile
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extract_dir = Path(zip_path).parent / 'cod10k_extracted'
            print(f"   Extracting to {extract_dir}...")
            zip_ref.extractall(extract_dir)
            
        # Now organize
        organize_dataset(str(extract_dir), cod10k_dir)
        
        # Cleanup
        shutil.rmtree(extract_dir)
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True


def organize_dataset(source_dir, cod10k_dir):
    """Organize extracted dataset."""
    cod10k_path = Path(cod10k_dir)
    source_path = Path(source_dir)
    
    # Create target directories
    for split in ['train', 'test']:
        for dtype in ['images', 'gts']:
            (cod10k_path / dtype / split).mkdir(parents=True, exist_ok=True)
    
    print("\n🔧 Organizing dataset structure...")
    
    # Copy images
    train_imgs, test_imgs = find_and_copy_images(
        source_path,
        cod10k_path / 'images' / 'train',
        cod10k_path / 'images' / 'test'
    )
    
    # Copy ground truth masks
    train_masks, test_masks = find_and_copy_images(
        source_path,
        cod10k_path / 'gts' / 'train',
        cod10k_path / 'gts' / 'test'
    )
    
    print(f"\n✓ Organization complete:")
    print(f"  Training images: {train_imgs}")
    print(f"  Test images: {test_imgs}")
    print(f"  Training masks: {train_masks}")
    print(f"  Test masks: {test_masks}")


def main():
    parser = argparse.ArgumentParser(description='Organize COD10K dataset')
    parser.add_argument('--source', type=str, help='Source directory or ZIP file')
    parser.add_argument('--output', type=str, default='data/COD10K', help='Output directory')
    parser.add_argument('--verify', action='store_true', help='Verify dataset after organization')
    
    args = parser.parse_args()
    
    if not args.source:
        print("Usage:")
        print("  python organize_cod10k.py --source /path/to/COD10K.zip --output data/COD10K")
        print("  python organize_cod10k.py --source /path/to/extracted/COD10K")
        return
    
    source_path = Path(args.source)
    
    if source_path.suffix == '.zip':
        organize_manual_download(str(source_path), args.output)
    else:
        organize_dataset(str(source_path), args.output)
    
    if args.verify:
        verify_dataset(args.output)


def verify_dataset(cod10k_dir):
    """Verify dataset is properly organized."""
    cod10k_path = Path(cod10k_dir)
    
    print(f"\n✓ Verifying dataset...")
    
    stats = {
        'train_images': len(list((cod10k_path / 'images' / 'train').glob('*'))),
        'test_images': len(list((cod10k_path / 'images' / 'test').glob('*'))),
        'train_masks': len(list((cod10k_path / 'gts' / 'train').glob('*'))),
        'test_masks': len(list((cod10k_path / 'gts' / 'test').glob('*'))),
    }
    
    print(f"\n📊 Dataset Statistics:")
    print(f"  Training images: {stats['train_images']:,}")
    print(f"  Test images: {stats['test_images']:,}")
    print(f"  Training masks: {stats['train_masks']:,}")
    print(f"  Test masks: {stats['test_masks']:,}")
    
    if stats['train_images'] == stats['train_masks'] and stats['test_images'] == stats['test_masks']:
        print(f"\n✓ Dataset is properly organized!")
        return True
    else:
        print(f"\n⚠ Warning: Check image/mask alignment")
        return False


if __name__ == "__main__":
    main()
