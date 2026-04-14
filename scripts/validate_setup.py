#!/usr/bin/env python3
"""
COD-Odisha Project Validation Script

Validates the project structure and dependencies before training.
Run this script to ensure everything is properly set up.

Usage:
    python validate_setup.py
"""

import sys
import os
from pathlib import Path

def check_directory_structure():
    """Check if all required directories exist."""
    print("\n" + "="*60)
    print("📁 Checking Directory Structure")
    print("="*60)
    
    required_dirs = [
        'backend',
        'backend/app',
        'backend/app/models',
        'backend/app/modules',
        'backend/datasets',
        'backend/utils',
        'model_training',
        'model_training/datasets',
        'model_training/configs',
        'frontend',
        'frontend/src',
        'data',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} (MISSING)")
            all_exist = False
    
    return all_exist


def check_required_files():
    """Check if all required files exist."""
    print("\n" + "="*60)
    print("📄 Checking Required Files")
    print("="*60)
    
    required_files = {
        'Backend': [
            'backend/__init__.py',
            'backend/app/__init__.py',
            'backend/app/models/__init__.py',
            'backend/app/modules/__init__.py',
            'backend/requirements.txt',
        ],
        'Training': [
            'model_training/__init__.py',
            'model_training/train.py',
            'model_training/evaluate.py',
            'model_training/export_onnx.py',
            'model_training/datasets/__init__.py',
            'model_training/datasets/odisha_cod_dataset.py',
            'model_training/datasets/augmentation.py',
            'model_training/configs/resnet50_config.yaml',
            'model_training/requirements.txt',
        ],
        'Frontend': [
            'frontend/package.json',
            'frontend/vite.config.js',
            'frontend/src/App.jsx',
        ],
        'Config': [
            '.gitignore',
            '.env.example',
            'pyproject.toml',
            'README.md',
            'SETUP.md',
            'QUICK_REFERENCE.md',
        ],
    }
    
    all_exist = True
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file_path in files:
            if Path(file_path).exists():
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ {file_path} (MISSING)")
                all_exist = False
    
    return all_exist


def check_python_packages():
    """Check if required Python packages are installed."""
    print("\n" + "="*60)
    print("📦 Checking Python Packages")
    print("="*60)
    
    required_packages = {
        'Core': ['torch', 'torchvision', 'numpy', 'PIL'],
        'Data': ['yaml', 'scipy', 'cv2'],
        'Training': ['tqdm'],
    }
    
    all_installed = True
    for category, packages in required_packages.items():
        print(f"\n{category}:")
        for package in packages:
            try:
                __import__(package)
                print(f"  ✓ {package}")
            except ImportError:
                print(f"  ✗ {package} (NOT INSTALLED)")
                all_installed = False
    
    return all_installed


def check_imports():
    """Check if main modules can be imported."""
    print("\n" + "="*60)
    print("🔗 Checking Module Imports")
    print("="*60)
    
    import_checks = [
        ('backend.app.models', 'Models'),
        ('backend.app.modules', 'Modules'),
    ]
    
    all_imports_ok = True
    for module_path, name in import_checks:
        try:
            sys.path.insert(0, str(Path.cwd()))
            __import__(module_path)
            print(f"✓ {name} ({module_path})")
        except ImportError as e:
            print(f"✗ {name} ({module_path})")
            print(f"  Error: {e}")
            all_imports_ok = False
        except Exception as e:
            print(f"⚠ {name} ({module_path})")
            print(f"  Warning: {e}")
    
    return all_imports_ok


def check_torch():
    """Check PyTorch installation and CUDA availability."""
    print("\n" + "="*60)
    print("🔥 Checking PyTorch & CUDA")
    print("="*60)
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"✓ CUDA available: Yes")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  Device count: {torch.cuda.device_count()}")
        else:
            print(f"⚠ CUDA available: No (CPU only)")
        
        return True
    except Exception as e:
        print(f"✗ PyTorch error: {e}")
        return False


def check_data_structure():
    """Check if data directories have expected structure."""
    print("\n" + "="*60)
    print("📊 Checking Data Structure")
    print("="*60)
    
    datasets = ['COD10K', 'CAMO', 'NC4K', 'OdishaCustom']
    found_any = False
    
    for dataset_name in datasets:
        dataset_path = Path('data') / dataset_name
        if dataset_path.exists():
            train_imgs = list((dataset_path / 'images' / 'train').glob('*')) if (dataset_path / 'images' / 'train').exists() else []
            test_imgs = list((dataset_path / 'images' / 'test').glob('*')) if (dataset_path / 'images' / 'test').exists() else []
            print(f"✓ {dataset_name}: {len(train_imgs)} train, {len(test_imgs)} test")
            found_any = True
        else:
            print(f"⚠ {dataset_name}: Not found (will be downloaded during training)")
    
    if not found_any:
        print("\n⚠ No datasets found in data/ directory")
        print("  Datasets need to be downloaded before training")
        print("  See SETUP.md for dataset download instructions")
    
    return found_any


def check_config():
    """Check if configuration files exist and are valid."""
    print("\n" + "="*60)
    print("⚙️  Checking Configuration")
    print("="*60)
    
    try:
        import yaml
        
        config_path = Path('model_training/configs/resnet50_config.yaml')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✓ Config file exists: resnet50_config.yaml")
            print(f"  Model: {config.get('model', {}).get('backbone', 'unknown')}")
            print(f"  Epochs: {config.get('training', {}).get('epochs', 'unknown')}")
            print(f"  Batch size: {config.get('training', {}).get('batch_size', 'unknown')}")
            return True
        else:
            print(f"✗ Config file not found: resnet50_config.yaml")
            return False
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False


def print_summary(results):
    """Print validation summary."""
    print("\n" + "="*60)
    print("📋 Validation Summary")
    print("="*60)
    
    checks = results
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for check_name, passed_check in checks.items():
        status = "✓ PASS" if passed_check else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your project is ready for training.")
        print("\nNext steps:")
        print("1. Review SETUP.md for detailed instructions")
        print("2. Download datasets (if not already done)")
        print("3. Run: python model_training/train.py --config model_training/configs/resnet50_config.yaml")
        return True
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before training.")
        return False


def main():
    """Run all validation checks."""
    print("\n" + "="*60)
    print("COD-Odisha Project Validation")
    print("="*60)
    
    results = {
        'Directory Structure': check_directory_structure(),
        'Required Files': check_required_files(),
        'Python Packages': check_python_packages(),
        'Module Imports': check_imports(),
        'PyTorch & CUDA': check_torch(),
        'Configuration': check_config(),
        'Data Structure': check_data_structure(),
    }
    
    success = print_summary(results)
    
    print("\n" + "="*60)
    print("For more information, see:")
    print("- SETUP.md: Complete setup guide")
    print("- QUICK_REFERENCE.md: Command reference")
    print("- PRE_TRAINING_CHECKLIST.md: Detailed checklist")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
