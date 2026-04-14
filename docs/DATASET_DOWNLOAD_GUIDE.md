# COD10K Dataset Download Guide

## Quick Start

### Option 1: Automated Download (Recommended)
```bash
cd "c:\Users\dasni\New folder\cod-odisha"
python download_cod10k.py
```

This will:
- ✓ Download the full COD10K dataset (~2.7 GB compressed)
- ✓ Extract and organize into proper directory structure
- ✓ Replace dummy images with real data
- ✓ Verify dataset integrity

**Estimated Time**: 30-60 minutes (depending on internet speed)

---

## Dataset Information

### COD10K Details
- **Type**: Camouflaged Object Detection Dataset
- **Training Images**: ~5000
- **Test Images**: ~1344
- **Total Size**: ~2.7 GB (compressed), ~5-6 GB (extracted)
- **Format**: JPEG images + PNG ground truth masks
- **Source**: https://github.com/DengPingFan/COD10K

### Directory Structure After Download
```
data/COD10K/
├── images/
│   ├── train/           (5000 training images)
│   └── test/            (1344 test images)
└── gts/
    ├── train/           (5000 training masks)
    └── test/            (1344 test masks)
```

---

## Alternative Download Options

### Option 2: Manual Download from GitHub
1. Visit: https://github.com/DengPingFan/COD10K/releases
2. Download `COD10K.zip` from the latest release
3. Place in a temporary folder
4. Run organization script:
   ```bash
   python organize_cod10k.py /path/to/COD10K.zip
   ```

### Option 3: Using wget/curl (Linux/Mac/WSL)
```bash
# Download
wget https://github.com/DengPingFan/COD10K/releases/download/v1.0/COD10K.zip

# Or with curl
curl -L -o COD10K.zip "https://github.com/DengPingFan/COD10K/releases/download/v1.0/COD10K.zip"

# Extract
unzip COD10K.zip
python download_cod10k.py
```

### Option 4: Faster Alternative - Use Smaller Dataset
If download speed is an issue, you can use these smaller COD datasets:
- **COCO-COD**: ~300 images with camouflaged objects
- **NC4K**: ~4121 images for camouflaged object detection
- **SINet-dataset**: ~6000 images

---

## What to Do After Download

### 1. Verify Dataset
```bash
python -c "
import os
from pathlib import Path

cod10k = Path('data/COD10K')
train_imgs = len(list((cod10k / 'images' / 'train').glob('*')))
test_imgs = len(list((cod10k / 'images' / 'test').glob('*')))
train_masks = len(list((cod10k / 'gts' / 'train').glob('*')))
test_masks = len(list((cod10k / 'gts' / 'test').glob('*')))

print(f'Training images: {train_imgs}')
print(f'Test images: {test_imgs}')
print(f'Training masks: {train_masks}')
print(f'Test masks: {test_masks}')
"
```

### 2. Start Training
```bash
python model_training/train.py --config model_training/configs/resnet50_config.yaml
```

### 3. Monitor Training
- Check terminal output for loss values
- Validation metrics printed at end of each epoch
- Checkpoints saved to `checkpoints/` directory

### 4. Expected Results
- **First epoch loss**: ~0.5-1.0 (will decrease)
- **Training time**: ~5-7 hours per epoch (CPU), ~30-60 min (GPU)
- **Full training (100 epochs)**: 20-30 hours (CPU), 8-12 hours (GPU)

---

## Troubleshooting

### Download Fails
- **Issue**: Network timeout or connection error
- **Solution**: 
  1. Increase timeout: `python download_cod10k.py --timeout 300`
  2. Use VPN if region-locked
  3. Download manually from GitHub releases

### Extraction Fails
- **Issue**: ZIP file corrupted
- **Solution**:
  1. Delete the corrupted file: `rm downloads/COD10K.zip`
  2. Re-run downloader
  3. Or manually download and verify checksum

### Disk Space Issues
- **Issue**: Not enough space for extraction (~6 GB needed)
- **Solution**:
  1. Free up disk space
  2. Use external drive
  3. Or use smaller dataset alternative (see Option 4 above)

### Permission Denied
- **Issue**: Cannot write to directory
- **Solution**:
  1. Run with admin privileges
  2. Check folder permissions: `icacls data\`
  3. Create fresh directory: `mkdir -p data/COD10K`

---

## Performance Expectations

### With Full Dataset (6344 images)
- **Training Speed**: 
  - CPU: ~2-3 seconds per image
  - GPU (NVIDIA RTX 3080): ~50-100ms per image
  
- **Epoch Duration**:
  - CPU (batch_size=8): ~30-40 minutes
  - GPU (batch_size=32): ~5-10 minutes

- **Convergence**:
  - Loss typically plateaus after 50-70 epochs
  - Best results at 80-100 epochs

### With Dummy Dataset (7 images)
- **Epoch Duration**: <1 second
- **Use Case**: Testing pipeline, debugging code
- **Limitation**: No real convergence, metrics are unrealistic

---

## Next Steps

1. **Download dataset**: `python download_cod10k.py` (takes 30-60 mins)
2. **Verify download**: Check statistics above
3. **Start training**: `python model_training/train.py --config model_training/configs/resnet50_config.yaml`
4. **Monitor progress**: Watch loss decrease over epochs
5. **Evaluate model**: `python model_training/evaluate.py --checkpoint checkpoints/best_model.pth`
6. **Export for deployment**: `python model_training/export_onnx.py --checkpoint checkpoints/best_model.pth`

---

## Technical Details

### Dataset Split Ratio
- **Training**: 5000 images (78.8%)
- **Testing**: 1344 images (21.2%)

### Annotation Format
- **Images**: JPEG format, variable resolution
- **Masks**: PNG format, binary (0/255 or 0/1)
- **Channel**: 3 channels (RGB) for images, 1 channel for masks

### Preprocessing in Training
- Resize: 352×352
- Normalization: ImageNet mean/std
- Augmentation: RandomFlip, ColorJitter, GaussianBlur

---

## Support

If you encounter issues:
1. Check dataset directory structure matches expected layout
2. Verify all files downloaded correctly
3. Ensure sufficient disk space (6+ GB)
4. Try alternative download method (manual from GitHub)
5. Check internet connection and firewall settings

---

**Ready to start training with real data!** 🚀
