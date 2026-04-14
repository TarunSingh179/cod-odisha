# Quick Reference Guide

## Essential Commands for Training

### Setup
```bash
# Create environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r model_training/requirements.txt
cd frontend && npm install && cd ..
```

### Training
```bash
# Standard training
cd model_training
python train.py --config configs/resnet50_config.yaml

# Resume from checkpoint
python train.py --config configs/resnet50_config.yaml --resume checkpoints/checkpoint_epoch_50.pth

# With custom config
python train.py --config configs/custom_config.yaml
```

### Evaluation
```bash
# Test set evaluation
python evaluate.py \
    --checkpoint checkpoints/best_model.pth \
    --config configs/resnet50_config.yaml \
    --split test \
    --save-results results.json

# Single dataset evaluation
python evaluate.py \
    --checkpoint checkpoints/best_model.pth \
    --config configs/resnet50_config.yaml
```

### Export
```bash
# Export to ONNX
python export_onnx.py \
    --checkpoint checkpoints/best_model.pth \
    --config configs/resnet50_config.yaml \
    --output cod_odisha.onnx

# Custom input size
python export_onnx.py \
    --checkpoint checkpoints/best_model.pth \
    --output model.onnx \
    --input-size 1 3 512 512
```

### Development
```bash
# Frontend dev server
cd frontend
npm run dev

# Frontend production build
npm run build
npm run preview

# TensorBoard monitoring
tensorboard --logdir=runs/
```

---

## Configuration Files

### Core Configs
- `model_training/configs/resnet50_config.yaml` - Main training config
- `.env` - Environment variables and secrets
- `pyproject.toml` - Project metadata

### Key Settings in YAML
```yaml
model:
  backbone: resnet50              # or resnet18
  
training:
  epochs: 100
  batch_size: 8                   # Reduce if OOM
  learning_rate: 0.0001
  
dataset:
  image_size: [352, 352]
  paths:
    cod10k_root: ./data/COD10K
    camo_root: ./data/CAMO
```

---

## Directory Structure Overview

```
cod-odisha/
├── backend/               # Model code
│   ├── app/
│   │   ├── models/       # Model definitions
│   │   └── modules/      # CCSIM, SGFL, Decoder
│   └── requirements.txt
│
├── model_training/       # Training pipeline
│   ├── train.py
│   ├── evaluate.py
│   ├── export_onnx.py
│   ├── configs/
│   ├── datasets/
│   └── requirements.txt
│
├── frontend/            # Web UI
│   └── package.json
│
├── data/               # Datasets (not in git)
│   ├── COD10K/
│   ├── CAMO/
│   ├── NC4K/
│   └── OdishaCustom/
│
└── checkpoints/       # Models (not in git)
    ├── best_model.pth
    └── checkpoint_*.pth
```

---

## Common Workflows

### 1. First Time Training
```bash
# 1. Setup
python -m venv venv && source venv/bin/activate
pip install -r model_training/requirements.txt

# 2. Prepare data
# Download and organize datasets in data/

# 3. Quick validation
cd model_training
python -c "from datasets.odisha_cod_dataset import build_dataset; print('✓')"

# 4. Train
python train.py --config configs/resnet50_config.yaml
```

### 2. Monitor Training
```bash
# In separate terminal
tensorboard --logdir=runs/
# Open http://localhost:6006
```

### 3. Evaluate Best Model
```bash
python evaluate.py \
    --checkpoint checkpoints/best_model.pth \
    --config configs/resnet50_config.yaml \
    --split test
```

### 4. Export for Deployment
```bash
python export_onnx.py \
    --checkpoint checkpoints/best_model.pth \
    --output cod_odisha.onnx
```

### 5. Resume Training
```bash
python train.py \
    --config configs/resnet50_config.yaml \
    --resume checkpoints/checkpoint_epoch_50.pth
```

---

## Performance Tuning

### If Training is Slow
```yaml
# In config.yaml
training:
  mixed_precision: true  # Enable (default)
  num_workers: 8         # Match CPU cores
augmentation:
  horizontal_flip: true
  vertical_flip: false   # Disable unused
```

### If Running Out of GPU Memory
```yaml
training:
  batch_size: 4          # Reduce from 8
  mixed_precision: true  # Keep enabled
augmentation:
  random_crop: false     # Disable if not needed
```

### For Faster Convergence
```yaml
training:
  epochs: 100            # Keep same
  batch_size: 16         # Increase if memory allows
  learning_rate: 0.0002  # Slightly higher
```

---

## Debugging

### Check CUDA
```bash
python -c "import torch; print(torch.cuda.is_available())"
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Test Dataset Loading
```bash
cd model_training
python -c "
from datasets.odisha_cod_dataset import build_dataset
config = {'name': 'COD10K', 'image_size': [352, 352], 'paths': {'cod10k_root': '../data/COD10K'}}
ds = build_dataset(config, split='train')
print(f'Loaded {len(ds)} samples')
"
```

### Check Model
```bash
python -c "
from backend.app.models import build_model
model = build_model(backbone='resnet50')
import torch
x = torch.randn(1, 3, 352, 352)
out = model(x)
print('Model works! Output keys:', out.keys())
"
```

---

## Metrics Explained

| Metric | Range | Meaning | Lower is Better? |
|--------|-------|---------|-----------------|
| **MAE** | [0, 1] | Mean Absolute Error | ✓ Yes |
| **F-measure** | [0, 1] | F-β score | ✗ No |
| **S-measure** | [0, 1] | Structure measure | ✗ No |
| **E-measure** | [0, 1] | Enhanced alignment | ✗ No |

### Example Results
```
F-measure:  0.85-0.95 (good)
S-measure:  0.80-0.90 (good)
E-measure:  0.80-0.90 (good)
MAE:        0.02-0.05 (good)
```

---

## Files to Know

### Important Python Files
- `train.py` - Main training script
- `evaluate.py` - Evaluation script
- `export_onnx.py` - Model export
- `backend/app/models/__init__.py` - Model architecture
- `backend/app/modules/__init__.py` - CCSIM, SGFL modules

### Important Config Files
- `resnet50_config.yaml` - Training config
- `.env.example` - Environment template
- `pyproject.toml` - Project metadata

### Important Data Files
- `data/[Dataset]/images/train/` - Training images
- `data/[Dataset]/gts/train/` - Training masks

---

## Tips & Best Practices

✅ **Do:**
- Save configs with meaningful names
- Commit code changes regularly
- Log experiments with timestamps
- Keep checkpoints organized
- Run evaluation on test set only

❌ **Don't:**
- Train on the full test set (use validation set)
- Delete checkpoints before evaluation
- Skip preprocessing/augmentation
- Use the same random seed for all runs
- Multiply batch size without adjusting learning rate

---

## Getting Help

1. Check `PRE_TRAINING_CHECKLIST.md`
2. Review `SETUP.md` for detailed guide
3. Run debug commands above
4. Check error messages carefully
5. Consult main `README.md`

---

**Last Updated:** 2024
**Quick Commands Version:** 1.0
