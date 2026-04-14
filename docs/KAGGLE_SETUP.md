# 🔐 Kaggle Setup Instructions

## Quick Setup (3 Steps)

### Step 1: Get Your Kaggle API Token
1. Go to: https://www.kaggle.com/settings/account
2. Click "Create New API Token"
3. This downloads `kaggle.json` file (~100 bytes)

### Step 2: Place Credentials File
The file needs to be in: `%USERPROFILE%\.kaggle\kaggle.json`

**For C:\Users\dasni\, that means:**
- Create folder: `C:\Users\dasni\.kaggle`
- Move `kaggle.json` there

**Option A: Using PowerShell (Recommended)**
```powershell
# Create .kaggle folder
mkdir "$env:USERPROFILE\.kaggle" -Force

# Copy kaggle.json to the folder
# (Select downloads/kaggle.json first, then:)
Copy-Item "C:\path\to\downloads\kaggle.json" "$env:USERPROFILE\.kaggle\kaggle.json"

# Verify
ls "$env:USERPROFILE\.kaggle\"
```

**Option B: Manual**
1. Press Win+R
2. Type: `%USERPROFILE%\.kaggle`
3. Create `.kaggle` folder
4. Paste `kaggle.json` into it

### Step 3: Accept Dataset Terms
1. Visit: https://www.kaggle.com/datasets/patrickberrill/camouflaged-object-detection
2. Click "Join" or accept the terms
3. Run the download script

## Then Download

Once credentials are set up:

```bash
cd "c:\Users\dasni\New folder\cod-odisha"
python download_from_kaggle.py
```

**This will:**
- Download 5000+ training images
- Download 1344+ test images
- Automatically organize into `data/COD10K/`
- Verify dataset integrity
- Ready for training!

## If You Don't Have Kaggle Account

Create one free at: https://www.kaggle.com/signup

Takes 2 minutes!

---

**After setup, run:** `python download_from_kaggle.py`
