# COD-Odisha: Setup & Training Guide

## Quick Start

### 1. Environment Setup

#### Clone the Repository
```bash
git clone <repo-url>
cd cod-odisha
```

#### Create Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Using conda
conda create -n cod-odisha python=3.10
conda activate cod-odisha
```

#### Install Dependencies

**Backend (Model Training)**
```bash
cd model_training
pip install -r requirements.txt
cd ..
```

**Frontend (Web Interface)**
```bash
cd frontend
npm install
cd ..
```

### 2. Prepare Dataset

#### Download Datasets
Create a `data/` directory and download the following datasets:

- **COD10K**: https://github.com/DengPingFan/COD10K
- **CAMO**: http://dpfan.net/camo/
- **NC4K**: https://github.com/lz118/NC4K-Part-aware-Salient-Object-Detection
- **OdishaCustom**: Your custom Odisha biodiversity dataset

#### Organize Data Structure
```
cod-odisha/
└── data/
    ├── COD10K/
    │   ├── images/
    │   │   ├── train/
    │   │   └── test/
    │   └── gts/
    │       ├── train/
    │       └── test/
    ├── CAMO/
    │   ├── images/
    │   │   ├── train/
    │   │   └── test/
    │   └── gts/
    │       ├── train/
    │       └── test/
    ├── NC4K/
    │   └── ...
    └── OdishaCustom/
        └── ...
```

### 3. Configuration

#### Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
```

Key configurations in `.env`:
- `CUDA_VISIBLE_DEVICES`: GPU device IDs
- `BATCH_SIZE`: Training batch size (default: 8)
- `LEARNING_RATE`: Initial learning rate (default: 0.0001)
- `EPOCHS`: Number of training epochs (default: 100)

#### Model Configuration
Edit `model_training/configs/resnet50_config.yaml`:

```yaml
model:
  backbone: resnet50          # or resnet18
  pretrained: true
  ccsim_out_channels: 128
  sgfl_out_channels: 64

training:
  epochs: 100
  batch_size: 8
  learning_rate: 0.0001
  
dataset:
  paths:
    cod10k_root: ./data/COD10K
    camo_root: ./data/CAMO
    nc4k_root: ./data/NC4K
    custom_odisha_root: ./data/OdishaCustom
```

---

## Training Guide

### Basic Training

```bash
cd model_training

# Single dataset training
python train.py --config configs/resnet50_config.yaml

# Resume from checkpoint
python train.py --config configs/resnet50_config.yaml --resume checkpoints/checkpoint_epoch_50.pth
```

### Output Structure
```
model_training/
└── checkpoints/
    ├── best_model.pth          # Best model on validation set
    ├── checkpoint_epoch_10.pth  # Periodic checkpoints
    ├── checkpoint_epoch_20.pth
    └── ...
```

### Training Monitoring

#### Using TensorBoard
```bash
tensorboard --logdir=runs/
# Open http://localhost:6006 in browser
```

#### Using Weights & Biases (Optional)
Edit `.env`:
```
USE_WANDB=true
WANDB_API_KEY=your_api_key
```

---

## Evaluation

### Evaluate on Test Set
```bash
python evaluate.py \
    --checkpoint checkpoints/best_model.pth \
    --config configs/resnet50_config.yaml \
    --split test \
    --save-results results.json
```

### Metrics Computed
- **F-measure**: F-beta score (β² = 0.3)
- **S-measure**: Structure measure
- **E-measure**: Enhanced alignment measure
- **MAE**: Mean Absolute Error
- **Precision & Recall**

---

## Model Export

### Export to ONNX
```bash
python export_onnx.py \
    --checkpoint checkpoints/best_model.pth \
    --config configs/resnet50_config.yaml \
    --output cod_odisha.onnx \
    --opset 13
```

Benefits of ONNX:
- Cross-platform compatibility
- Optimized inference on CPUs/GPUs
- Edge device deployment
- Language-agnostic (C++, Java, C#, Python)

---

## Frontend Development

### Development Server
```bash
cd frontend
npm run dev
# Opens http://localhost:5173
```

### Production Build
```bash
npm run build
npm run preview
```

### Features
- Image upload and preview
- Real-time camouflaged object detection
- Bilingual output (English/Odia)
- Result visualization with masks and heatmaps
- Scene-specific detection (forest, water, agricultural)

---

## Project Structure

```
cod-odisha/
├── backend/                  # Model inference & API
│   ├── app/
│   │   ├── models/          # Model definitions
│   │   └── modules/         # CCSIM, SGFL modules
│   ├── datasets/
│   ├── utils/
│   └── requirements.txt
│
├── model_training/          # Training scripts
│   ├── train.py            # Main training script
│   ├── evaluate.py         # Evaluation script
│   ├── export_onnx.py      # ONNX export
│   ├── datasets/           # Data loading
│   ├── configs/            # Config files
│   └── requirements.txt
│
├── frontend/               # Web interface
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── data/                   # Datasets (git-ignored)
├── .gitignore
├── .env.example
└── README.md
```

---

## Model Architecture

### CODModel (Main)
```
Input Image (B, 3, H, W)
        ↓
Backbone (ResNet50/18)
[Extracts multi-scale features: C2, C3, C4, C5]
        ↓
CCSIM (Cross-Scale Channel Similarity & Interaction)
[Aligns and fuses multi-scale features with channel attention]
        ↓
SGFL (Semantic Guided Feature Learning)
[Enhances objects, suppresses background, refines boundaries]
        ↓
Boundary-Aware Decoder
[Progressive upsampling with boundary refinement]
        ↓
Output: Mask (B, 1, H, W) + Boundary (B, 1, H, W)
```

### Key Components

#### CCSIM Module
- Feature alignment across scales
- Channel attention mechanisms
- Cross-scale interaction

#### SGFL Module
- Semantic guidance branches
- Background suppression
- Object and boundary enhancement

#### BoundaryAwareDecoder
- Progressive 2x upsampling
- Boundary-aware loss
- Sharp edge predictions

---

## Hyperparameter Tuning

### Recommended Settings
```yaml
# For fast training (ResNet18)
model:
  backbone: resnet18
training:
  batch_size: 16
  learning_rate: 0.0002
  epochs: 50

# For accurate training (ResNet50)
model:
  backbone: resnet50
training:
  batch_size: 8
  learning_rate: 0.0001
  epochs: 100

# For limited GPU memory
training:
  batch_size: 4
  accumulation_steps: 2
  mixed_precision: true
```

### Loss Weights
```yaml
loss_weights:
  bce: 1.0          # Binary Cross Entropy
  iou: 1.0          # Intersection over Union
  boundary: 0.5     # Boundary refinement
  semantic: 0.3     # Semantic guidance
```

---

## Troubleshooting

### GPU Memory Issues
```bash
# Reduce batch size in config
batch_size: 4  # from 8

# Enable mixed precision (already enabled by default)
mixed_precision: true
```

### Dataset Not Found
```bash
# Check data directory structure
python -c "from datasets.odisha_cod_dataset import build_dataset; print('Dataset loaded')"
```

### Import Errors
```bash
# Ensure proper path configuration
python -c "import sys; sys.path.insert(0, '.'); from backend.app.models import build_model"
```

### CUDA Out of Memory
1. Reduce `batch_size` in config
2. Enable `mixed_precision: true`
3. Reduce `image_size` from 352 to 320 or 288

---

## Performance Benchmarks

### Inference Speed (Single Image)
- ResNet50 on GPU: ~50-100 ms
- ResNet50 on CPU: ~500-1000 ms
- ResNet18 on GPU: ~30-50 ms

### Model Sizes
- ResNet50 model: ~105 MB
- ResNet18 model: ~45 MB
- ONNX optimized: ~50-60% of original

---

## Citation & References

If you use COD-Odisha in your research, please cite:

```bibtex
@software{cododisha2024,
  title={COD-Odisha: Camouflaged Object Detection for Odisha Biodiversity},
  author={Your Team},
  year={2024},
  url={https://github.com/your-org/cod-odisha}
}
```

### Related Papers
- DengPingFan et al. - "Camouflaged Object Detection" (CVPR 2021)
- He et al. - "Deep Residual Learning" (CVPR 2016)

---

## Support & Contribution

For issues, questions, or contributions:
1. Create an issue on GitHub
2. Submit a pull request
3. Check existing documentation

## License

MIT License - see LICENSE file for details
