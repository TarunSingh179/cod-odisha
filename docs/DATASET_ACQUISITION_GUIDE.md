# COD10K Dataset Acquisition Guide

## Status
- ✓ Model: Ready (ResNet50 + CCSIM + SGFL)
- ✓ Training pipeline: Ready
- ✗ Large dataset: Not yet acquired (Kaggle API blocked)
- ✓ Dummy dataset: Available (7 images for testing)

## Option 1: Use Dummy Data (Immediate)
Start training right away with the 7 dummy images to validate everything works:

```bash
python model_training/train.py --config model_training/configs/resnet50_config.yaml
```

**Pros:**
- Runs immediately
- Validates entire pipeline works
- Takes ~10 seconds per epoch

**Cons:**
- Small dataset (5 train, 2 test)
- Not useful for real model evaluation

## Option 2: Kaggle (Currently Blocked)
The Kaggle API endpoint is returning 403 Forbidden. To fix this:

1. Log in to https://www.kaggle.com
2. Find dataset: "COD-10K" or "Camouflaged Object Detection"
3. Accept terms/conditions if prompted
4. Download manually or try the script again

Script to retry:
```bash
python download_from_kaggle.py
```

## Option 3: Manual Browser Download (Recommended)
### 3A. Try these dataset sources:

**GitHub (Official):**
- Search: "COD10K" or "Camouflaged Object Detection" on GitHub
- Alternative: Check researcher's personal pages for uploads

**Kaggle Datasets:**
- https://www.kaggle.com/datasets
- Search: "camouflaged object detection" or "COD10K"
- Download manually from website

**Research Paper Resources:**
- Check the original paper: "Searching for Camouflaged Objects in the Wild"
- Author pages often have dataset links
- Supplementary materials may have download URLs

**Baidu Cloud (If you have access):**
- Code appears to be: `cod4`
- Would be faster if accessible from your region

### 3B. Once You Have the Dataset:

1. **Download the ZIP file** to your computer
2. **Save it** to: `downloads/COD10K.zip`
3. **Run the organizer:**
   ```bash
   python organize_cod10k.py --source downloads/COD10K.zip --verify
   ```
4. **Start training:**
   ```bash
   python model_training/train.py --config model_training/configs/resnet50_config.yaml
   ```

## Option 4: Create Synthetic Dataset
Generate more training samples from existing dummy data:

```python
from model_training.datasets.augmentation import AugmentationPipeline
import shutil
from pathlib import Path

augmenter = AugmentationPipeline(strength=0.7)
source = Path("data/COD10K/images/train")
target = Path("data/COD10K_augmented")

for img_path in source.glob("*.jpg"):
    for i in range(5):  # 5 augmentations per image
        augmented = augmenter.augment(img_path)
        augmented.save(target / f"{img_path.stem}_aug_{i}.jpg")
```

## Expected Directory Structure

Once organized, your dataset should look like:

```
data/COD10K/
├── images/
│   ├── train/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ... (5000+ images)
│   └── test/
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ... (1344 images)
└── gts/
    ├── train/
    │   ├── image1.png
    │   ├── image2.png
    │   └── ... (5000+ masks)
    └── test/
        ├── image1.png
        ├── image2.png
        └── ... (1344 masks)
```

## Verify Dataset
```bash
python dataset_status.py
```

Expected output:
```
Training: 5000+ images + 5000+ masks
Test: 1344 images + 1344 masks
Status: ✓ Ready to train
```

## Training Command
Once dataset is ready:

```bash
python model_training/train.py \
  --config model_training/configs/resnet50_config.yaml \
  --epochs 100 \
  --batch-size 8 \
  --learning-rate 0.001
```

## Timeline Estimates

| Dataset Size | Download | Organize | Per Epoch | 100 Epochs |
|---|---|---|---|---|
| Dummy (7 images) | Already in repo | Done | 10 sec | 17 min |
| COD10K (6350 images) | 30-60 min | 5 min | 30-40 min | 50-70 hours |

## Help & Troubleshooting

**Dataset won't organize:**
```bash
# Get help
python organize_cod10k.py --help

# Try with detailed logging
python organize_cod10k.py --source downloads/COD10K.zip --verbose
```

**Training crashes:**
Check that all image/mask pairs exist:
```bash
python verify_dataset_integrity.py
```

**Need more dummy data for testing:**
```bash
# Generate synthetic augmentations
python generate_synthetic_dataset.py --factor 10
```

## Summary

1. **Right now:** Run training with dummy data to validate everything works
2. **Soon:** Download real COD10K dataset from any source above
3. **Next:** Organize with our scripts and start training
4. **Result:** Deploy trained model for production use

All infrastructure is ready. Just need the dataset!
