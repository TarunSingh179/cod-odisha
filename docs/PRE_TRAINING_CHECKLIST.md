# Pre-Training Checklist

Use this checklist to ensure your project is ready for training.

## ✅ Project Structure
- [ ] `backend/` directory created with models and modules
- [ ] `model_training/` has all necessary scripts
- [ ] `frontend/` has dependencies installed
- [ ] `data/` directory created with subdirectories
- [ ] All `__init__.py` files present in Python packages

## ✅ Installation & Setup
- [ ] Virtual environment created and activated
- [ ] Backend dependencies installed: `pip install -r model_training/requirements.txt`
- [ ] Frontend dependencies installed: `npm install` in frontend/
- [ ] Python version 3.9+
- [ ] PyTorch 2.0+ installed (with CUDA if using GPU)

## ✅ Dataset Preparation
- [ ] COD10K dataset downloaded and extracted to `data/COD10K/`
- [ ] CAMO dataset downloaded and extracted to `data/CAMO/`
- [ ] NC4K dataset downloaded and extracted to `data/NC4K/`
- [ ] OdishaCustom dataset prepared (if available)
- [ ] Dataset structure verified:
  ```
  data/[Dataset]/
  ├── images/
  │   ├── train/
  │   └── test/
  └── gts/
      ├── train/
      └── test/
  ```
- [ ] Image and ground truth masks paired correctly
- [ ] At least 100 train samples and 50 test samples per dataset

## ✅ Configuration
- [ ] `.env` file created from `.env.example`
- [ ] GPU settings configured (CUDA_VISIBLE_DEVICES)
- [ ] Batch size adjusted based on GPU memory (8 = ~11GB, 4 = ~6GB)
- [ ] Model config reviewed: `model_training/configs/resnet50_config.yaml`
- [ ] Data paths updated to match your setup
- [ ] Learning rate appropriate for dataset size

## ✅ Hardware & Performance
- [ ] GPU available (CUDA) or CPU ready for training
- [ ] At least 50GB free disk space (for data + checkpoints)
- [ ] RAM: 16GB+ recommended
- [ ] Run quick test: `python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"`

## ✅ Validation Tests
- [ ] Import test:
  ```bash
  python -c "from backend.app.models import build_model; print('✓ Models load correctly')"
  ```
- [ ] Dataset test:
  ```bash
  cd model_training && python -c "from datasets.odisha_cod_dataset import build_dataset; print('✓ Dataset loads correctly')"
  ```
- [ ] Config test:
  ```bash
  cd model_training && python train.py --config configs/resnet50_config.yaml 2>&1 | head -20
  ```

## 📋 Training Parameters Check
- [ ] `epochs`: Recommended 50-100
- [ ] `batch_size`: 4-16 depending on GPU
- [ ] `learning_rate`: 0.0001 for ResNet50
- [ ] `image_size`: 352x352 standard
- [ ] `validation_interval`: 1 (validate every epoch)
- [ ] `mixed_precision`: true (recommended for speed)

## 🚀 Pre-Training Steps
1. [ ] Run quick 5-sample training test:
   ```bash
   # Modify config to use only 5 samples to test pipeline
   python train.py --config configs/resnet50_config.yaml
   # Stop after 2-3 epochs (Ctrl+C)
   ```
2. [ ] Check checkpoint format:
   ```bash
   python -c "import torch; ckpt = torch.load('checkpoints/best_model.pth'); print('Keys:', ckpt.keys())"
   ```
3. [ ] Test evaluation script:
   ```bash
   python evaluate.py --checkpoint checkpoints/best_model.pth --config configs/resnet50_config.yaml --split test
   ```

## 📊 Monitoring Setup
- [ ] TensorBoard installed: `pip install tensorboard`
- [ ] Weights & Biases optional: `pip install wandb`
- [ ] Logging directory readable/writable
- [ ] Results directory for metrics

## 🔄 Resuming Training
- [ ] Save checkpoint paths recorded
- [ ] Resume command tested: `python train.py --config configs/resnet50_config.yaml --resume checkpoints/checkpoint_epoch_10.pth`

## ✨ Final Verification
- [ ] Project structure is complete
- [ ] All imports work correctly
- [ ] Dataset loads without errors
- [ ] At least 1 training step completes successfully
- [ ] Checkpoints save correctly
- [ ] Evaluation script runs

## 🎯 Ready to Train!
```bash
cd model_training
python train.py --config configs/resnet50_config.yaml
```

Expected output:
```
============================================================
COD-Odisha Training
============================================================
Config: configs/resnet50_config.yaml
Model: resnet50
Epochs: 100
Batch size: 8
============================================================
[Dataset] Loading training data...
[Dataset] Loading validation data...
Train samples: XXX
Val samples: XXX

Epoch 1/100
----------------------------------------
  Batch 0/XXX: Loss=X.XXXX, BCE=X.XXXX, IoU=X.XXXX
  ...
```

---

## Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `CUDA out of memory` | Reduce batch_size to 4 or 2 |
| `Module not found` | Ensure `__init__.py` files exist in all packages |
| `Dataset not found` | Check data path matches config.yaml |
| `Import errors` | Verify sys.path entries in scripts |
| `Slow training` | Enable mixed_precision: true in config |
| `Low GPU utilization` | Increase batch_size or num_workers |

### Debug Commands

```bash
# Check environment
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'Devices: {torch.cuda.device_count()}')"

# Test imports
python -c "from backend.app.models import build_model; m = build_model(); print('✓ Models work')"

# List available GPUs
nvidia-smi

# Check dataset loading
cd model_training && python datasets/odisha_cod_dataset.py
```

---

## Performance Tips

1. **Increase training speed:**
   - Set `mixed_precision: true` in config
   - Increase `num_workers` to CPU core count
   - Use `pin_memory: true`

2. **Improve accuracy:**
   - Train longer (100+ epochs)
   - Use larger batch sizes (8-16)
   - Add more augmentation

3. **Reduce memory usage:**
   - Decrease batch_size
   - Reduce image_size to 320
   - Disable mixed_precision if using CPU

---

Generated: 2024
For questions, refer to SETUP.md
