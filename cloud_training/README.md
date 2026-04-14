# ☁️ COD-Odisha Cloud Training Guide

> Train the camouflaged object detection model **for free** on cloud GPUs instead of your local machine.

## 🎯 Quick Comparison

| Feature | Google Colab | Kaggle |
|---------|-------------|--------|
| **GPU** | NVIDIA T4 (16GB) | NVIDIA P100 (16GB) |
| **Free GPU Time** | ~12 hrs/day | 30 hrs/week |
| **Storage** | 100GB disk + Google Drive | 20GB output |
| **CPU Cores** | 2 | 4 |
| **RAM** | 12GB | 13GB |
| **Best For** | Quick experiments | Full training runs |

---

## 🚀 Option 1: Google Colab (Recommended)

### Step 1: Open Colab
1. Go to [Google Colab](https://colab.research.google.com)
2. Click **File → New Notebook**

### Step 2: Enable GPU
1. Click **Runtime → Change runtime type**
2. Select **T4 GPU**
3. Click **Save**

### Step 3: Upload and Run

Paste this into the first cell:

```python
# Upload the training script
from google.colab import files
uploaded = files.upload()  # Upload colab_train.py
```

Or clone the repo:

```python
!git clone https://github.com/YOUR_USERNAME/cod-odisha.git
%cd cod-odisha
```

Paste this into the next cell:

```python
# Install dependencies
!pip install -q torch torchvision scipy pillow pyyaml tqdm

# Run training
!python cloud_training/colab_train.py
```

### Step 4: Monitor Training
- Training logs print to the notebook output
- Checkpoints auto-save to Google Drive at `/MyDrive/cod-odisha-checkpoints/`

### Step 5: Download Trained Model

```python
# Download best model from Colab
from google.colab import files
files.download('/content/drive/MyDrive/cod-odisha-checkpoints/best_model.pth')
```

---

## 📊 Option 2: Kaggle

### Step 1: Setup Dataset
1. Go to [Kaggle](https://www.kaggle.com)
2. Go to **Datasets** → Search for **"COD10K"**
3. Click **New Notebook** on the dataset page

### Step 2: Enable GPU
1. In the notebook sidebar, click **Settings**
2. Under **Accelerator**, select **GPU P100**

### Step 3: Run Training

Paste the entire contents of `kaggle_train.py` into a cell, or:

```python
# If you've added the cod-odisha repo as a dataset
import sys
sys.path.insert(0, '/kaggle/input/cod-odisha')
exec(open('/kaggle/input/cod-odisha/cloud_training/kaggle_train.py').read())
```

### Step 4: Download Results

After training completes:
1. Go to your notebook's **Output** tab
2. Download `best_model.pth` from the output files

---

## 📦 Using Your Trained Model Locally

Once you've downloaded `best_model.pth`:

```bash
# Place in checkpoints directory
mkdir -p checkpoints
mv ~/Downloads/best_model.pth checkpoints/

# Run evaluation
cd cod-odisha
python model_training/evaluate.py \
  --checkpoint checkpoints/best_model.pth \
  --config model_training/configs/resnet50_config.yaml

# Start the backend with your model
cd backend
uvicorn app.main:app --reload --port 8000
```

---

## ⚙️ Training Configuration

Both scripts use optimized defaults. To customize, edit the config dict at the bottom of each script:

```python
CONFIG = {
    'backbone': 'resnet50',    # or 'resnet18' for faster training
    'epochs': 100,             # reduce for quick tests
    'batch_size': 8,           # increase if GPU memory allows
    'lr': 1e-4,                # learning rate
    'image_size': (352, 352),  # input resolution
    'mixed_precision': True,   # AMP for faster training
}
```

### Estimated Training Times

| Epochs | Colab (T4) | Kaggle (P100) |
|--------|-----------|---------------|
| 10 | ~1 hour | ~45 min |
| 50 | ~5 hours | ~4 hours |
| 100 | ~10 hours | ~8 hours |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "CUDA out of memory" | Reduce `batch_size` to 4 |
| "Dataset not found" | Follow dataset setup steps above |
| "Runtime disconnected" | Colab disconnects after ~90 min idle — keep tab active |
| "GPU quota exceeded" | Wait 24h (Colab) or use Kaggle as backup |

---

## 💡 Pro Tips

1. **Use Colab Pro** ($10/month) for longer sessions and better GPUs (A100)
2. **Kaggle competitions** often have bonus GPU hours
3. **Checkpoint frequently** — cloud sessions can disconnect
4. **Mixed precision** is enabled by default for ~2x speedup
5. Start with `epochs=10` to verify everything works before full training
