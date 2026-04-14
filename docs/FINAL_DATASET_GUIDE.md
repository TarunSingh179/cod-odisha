# 🎯 COD10K Dataset - Complete Download Guide

## ✅ Final Status

Kaggle API is configured and working, but the specific dataset may not be publicly available on Kaggle, or requires manual acceptance of terms.

**Recommendation: Use GitHub (Official Source) instead**

---

## 📥 BEST OPTION: Download from GitHub (Official)

### Step 1: Go to GitHub
Visit: https://github.com/DengPingFan/COD10K

### Step 2: Download ZIP
- Click green **"Code"** button
- Click **"Download ZIP"**
- This downloads ~2.7 GB

### Step 3: Save File
Move the downloaded file to:
```
c:\Users\dasni\New folder\cod-odisha\downloads\COD10K.zip
```

### Step 4: Organize Dataset
```bash
cd "c:\Users\dasni\New folder\cod-odisha"
python organize_cod10k.py --source downloads/COD10K.zip --verify
```

### Step 5: Start Training
```bash
python model_training/train.py --config model_training/configs/resnet50_config.yaml
```

**Time estimate: 2-3 minutes total setup after download**

---

## 🇨🇳 ALTERNATIVE: Baidu Cloud (China - Faster)

For users in mainland China (faster speeds):

### Link
https://pan.baidu.com/s/1Xnxc8nkWqfKhMCOJBOXQ8g

### Code
`cod4`

### Steps
1. Visit link, enter code
2. Download COD10K.zip
3. Save to: `downloads/COD10K.zip`
4. Run: `python organize_cod10k.py --source downloads/COD10K.zip --verify`

---

## 🔎 Kaggle Available Options

If you prefer Kaggle, search for these datasets:

1. **Camouflaged Object Detection** (multiple versions available)
2. **Animal Segmentation** datasets
3. **Medical Imaging** datasets (similar format)

To use any Kaggle dataset:
```bash
# Download any COD-related dataset from Kaggle
kaggle datasets download -d [dataset-name]

# Organize it
python organize_cod10k.py --source downloads/[dataset-name].zip --verify
```

---

## 📊 Current Setup Status

✅ **Installed:**
- Virtual environment (Python 3.14.4)
- PyTorch 2.0+
- All training dependencies
- Kaggle API (ready to use)

✅ **Ready to Train:**
- With 7 dummy images (instant)
- With ~6000 real images (from download)

---

## 🚀 RECOMMENDED WORKFLOW

1. **Download COD10K.zip from GitHub** (~30-60 min)
   - https://github.com/DengPingFan/COD10K/releases
   - Or Code → Download ZIP

2. **Organize the dataset** (~5 min)
   ```bash
   python organize_cod10k.py --source downloads/COD10K.zip --verify
   ```

3. **Start training immediately** (starts in seconds)
   ```bash
   python model_training/train.py --config model_training/configs/resnet50_config.yaml
   ```

**Total Time:** ~1-2 hours first time (includes download), then continuous training

---

## 💡 Quick Facts

- **Full COD10K Dataset Size:** 2.7 GB (zip), 6 GB (extracted)
- **Images:** 5000 training + 1344 test
- **Training Time (100 epochs):** 
  - CPU: 30-50 hours
  - GPU: 8-12 hours
- **Model:** ResNet50 + CCSIM + SGFL (25.1M parameters)

---

## ✨ You're All Set!

Everything is configured and ready. Just need to:
1. Download the dataset (GitHub or Baidu)
2. Run organize script
3. Start training

**No more setup needed!**

---

## 📝 Files Available to You

- `organize_cod10k.py` - Handles any dataset format
- `START_TRAINING.py` - Shows training options
- `dataset_status.py` - Check status anytime
- `complete_pipeline_test.py` - Validate pipeline
- All training scripts ready in `model_training/`

Ready to proceed? Download from GitHub and run the organize script!
