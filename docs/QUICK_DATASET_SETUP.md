# Quick Guide: Download Full COD10K Dataset

## 📥 Step 1: Automated Download (Simplest Method)

Run this command from the project root:

```bash
cd "c:\Users\dasni\New folder\cod-odisha"
python download_cod10k.py
```

**What it does:**
- Downloads COD10K.zip (~2.7 GB) 
- Extracts automatically
- Organizes into proper directory structure
- Replaces dummy images with real data
- Verifies dataset integrity

**Estimated time:** 30-60 minutes (depends on internet speed)

---

## 🔗 Step 2: Manual Download (If Automated Fails)

If automated download doesn't work:

1. **Visit the official source:** https://github.com/DengPingFan/COD10K
2. **Download:**
   - Go to **Releases** tab
   - Download the latest `COD10K.zip` release
   - Save to: `c:\Users\dasni\New folder\cod-odisha\downloads\`

3. **Organize:** 
```bash
cd "c:\Users\dasni\New folder\cod-odisha"
python organize_cod10k.py --source downloads/COD10K.zip --output data/COD10K --verify
```

---

## 🚀 Step 3: Verify & Start Training

Check dataset is properly downloaded:
```bash
python -c "
from pathlib import Path
cod10k = Path('data/COD10K')
print('Training images:', len(list((cod10k / 'images' / 'train').glob('*'))))
print('Test images:', len(list((cod10k / 'images' / 'test').glob('*'))))
"
```

**Expected output:**
```
Training images: 5000+
Test images: 1000+
```

Then start training:
```bash
python model_training/train.py --config model_training/configs/resnet50_config.yaml
```

---

## 💡 Alternative: Use Smaller Dataset (Faster Setup)

If you need to get started quickly without downloading 2.7 GB:

### Option A: Use Current Dummy Dataset
```bash
# Run training with 7 dummy images to test pipeline
python model_training/train.py --config model_training/configs/resnet50_config.yaml
# Completes in seconds, useful for debugging
```

### Option B: Download Smaller COD Dataset
Create a file `download_smaller_dataset.py` with:

```python
# Example: Download smaller COD4K dataset (~500 MB)
# Or use COCO-COD, NC4K, or SINet datasets
# (Instructions for these available upon request)
```

---

## 📊 Dataset Information

**Full COD10K Dataset:**
- Size: 2.7 GB compressed, ~6 GB extracted
- Training images: ~5000
- Test images: ~1344  
- Format: JPEG images + PNG masks
- Total files: ~12,700
- Download time: 30-60 min (typical broadband)
- Extraction time: 5-10 min

---

## ⚠️ Troubleshooting

### "Download fails"
```bash
# Try manual download:
# 1. Go to https://github.com/DengPingFan/COD10K/releases
# 2. Download COD10K.zip manually
# 3. Place in downloads/ folder
# 4. Run: python organize_cod10k.py --source downloads/COD10K.zip
```

### "Not enough disk space"
```bash
# Check available space:
powershell -c "Get-Volume C: | Select-Object SizeRemaining"

# Need: 6+ GB free space
```

### "Extraction fails"
```bash
# Delete corrupted file and retry:
del downloads\COD10K.zip
python download_cod10k.py
```

---

## 🎯 My Recommendation

**For fastest, most reliable setup:**

1. **Manual download from GitHub:**
   - Go to: https://github.com/DengPingFan/COD10K/releases
   - Download `COD10K.zip` 
   - Save to `downloads/` folder

2. **Use organizer:**
   ```bash
   python organize_cod10k.py --source downloads/COD10K.zip --verify
   ```

3. **Start training:**
   ```bash
   python model_training/train.py --config model_training/configs/resnet50_config.yaml
   ```

This gives you:
- ✅ Full control over download
- ✅ Clear progress tracking
- ✅ Reliable organization
- ✅ Real data for meaningful training

---

## 📋 What Happens After Download

Your directory will look like:
```
cod-odisha/
├── data/
│   └── COD10K/
│       ├── images/
│       │   ├── train/    (5000 images)
│       │   └── test/     (1344 images)
│       └── gts/
│           ├── train/    (5000 masks)
│           └── test/     (1344 masks)
├── model_training/
│   ├── train.py
│   ├── evaluate.py
│   └── configs/
├── downloads/          (temporary, can delete after)
└── [other project files]
```

Then you can start training immediately!

---

**Next Actions:**
1. Choose download method (automated or manual)
2. Run download/organization
3. Verify dataset exists
4. Start training!

Let me know if you need help with any step! 🚀
