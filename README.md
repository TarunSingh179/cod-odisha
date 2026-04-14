# 🦎 COD-Odisha: Camouflaged Object Detection for Odisha Biodiversity

> A deep learning system for detecting camouflaged animals, pests, and aquatic species in Odisha's diverse ecosystems — from Simlipal Tiger Reserve to Chilika Lake paddy fields.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![PyTorch](https://img.shields.io/badge/PyTorch-2.x-orange) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green) ![React](https://img.shields.io/badge/React-18-61DAFB) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌿 Overview

Existing object detection systems fail on camouflaged objects because they exploit visual similarity to the background. COD-Odisha is the **first camouflaged object detection system tailored for Odisha's flora and fauna**, directly addressing:

| Ecosystem | Application |
|-----------|------------|
| 🐯 Simlipal Tiger Reserve | Wildlife monitoring & poaching prevention |
| 🦆 Chilika Lake | Aquatic species survey & conservation |
| 🌾 Paddy Fields (Kandhamal) | Agricultural pest detection |
| 🌳 Forest Floor Biodiversity | Species cataloguing |
| 🌊 Bhitarkanika Mangroves | Mangrove ecosystem monitoring |

---

## ⚡ Quick Start — Development Setup

### One-Command Setup (Windows)

```powershell
# Run from the project root
powershell -ExecutionPolicy Bypass -File dev_setup.ps1
```

This will automatically:
- Create Python virtual environment
- Install backend + frontend dependencies
- Extract dataset from `downloads/archive.zip`
- Create `.env` configuration

### Start Development Servers

```powershell
powershell -ExecutionPolicy Bypass -File dev_start.ps1
```

Then open:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Manual Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## ☁️ Cloud Training (Recommended)

Train the model on **free cloud GPUs** instead of your local machine:

| Platform | GPU | Free Time | Script |
|----------|-----|-----------|--------|
| **Google Colab** | T4 (16GB) | ~12 hrs/day | `cloud_training/colab_train.py` |
| **Kaggle** | P100 (16GB) | 30 hrs/week | `cloud_training/kaggle_train.py` |

### Quick Start — Google Colab

1. Open [Google Colab](https://colab.research.google.com)
2. Upload `cloud_training/colab_train.py`
3. Set **Runtime → T4 GPU**
4. Run the script — checkpoints save to Google Drive

### Quick Start — Kaggle

1. Open [Kaggle](https://www.kaggle.com) → New Notebook
2. Add COD10K dataset → Set GPU to P100
3. Paste `cloud_training/kaggle_train.py` content
4. Run — outputs save to `/kaggle/working/`

📖 **Full guide**: See [cloud_training/README.md](cloud_training/README.md)

---

## 🧠 Model Architecture

```
Natural Image (Input)
        ↓
Backbone Network (ResNet50 / Res2Net50)
[Low-level + High-level feature extraction]
        ↓
Multi-Scale Feature Extraction (C2–C5)
        ↓
Cross-Scale Channel Similarity & Interaction Module (CCSIM)
[Feature alignment + cross-scale fusion]
        ↓
Semantic Guided Feature Learning (SGFL)
[Background suppression + Object enhancement + Boundary enhancement]
        ↓
Coarse Prediction → Boundary Refinement
        ↓
🎯 Camouflaged Object Mask
```

### Key Modules

- **CCSIM** (Cross-Scale Channel Similarity & Interaction Module): Aligns and fuses multi-scale feature maps using channel attention and cross-scale interaction
- **SGFL** (Semantic Guided Feature Learning): Uses semantic guidance to suppress background noise and enhance object/boundary regions
- **Boundary-Aware Decoder**: Progressive upsampling with boundary loss to improve edge delineation

---

## 🗂️ Project Structure

```
cod-odisha/
├── cloud_training/             # ☁️ Cloud GPU training scripts
│   ├── colab_train.py          # Google Colab (T4 GPU)
│   ├── kaggle_train.py         # Kaggle (P100 GPU)
│   └── README.md               # Cloud training guide
│
├── backend/                    # FastAPI inference server
│   ├── app/
│   │   ├── models/             # COD model (CCSIM + SGFL + Decoder)
│   │   ├── modules.py          # Core modules
│   │   └── ...
│   └── requirements.txt
│
├── frontend/                   # React + TailwindCSS web app
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   ├── package.json
│   └── vite.config.js
│
├── model_training/             # PyTorch training pipeline
│   ├── datasets/
│   ├── configs/
│   ├── train.py
│   └── evaluate.py
│
├── data/                       # Dataset (gitignored)
│   └── COD10K/
│       ├── images/train|test/
│       └── gts/train|test/
│
├── dev_setup.ps1               # One-command dev environment setup
├── dev_start.ps1               # Start backend + frontend
├── setup_data.py               # Extract dataset from archive
└── README.md
```

---

## 📊 Local Training

If you prefer local training (requires CUDA GPU):

```bash
# Setup dataset first
python setup_data.py --verify

# Train
python model_training/train.py --config model_training/configs/resnet50_config.yaml

# Evaluate
python model_training/evaluate.py \
  --checkpoint checkpoints/best_model.pth \
  --config model_training/configs/resnet50_config.yaml
```

### Supported Datasets
- **CAMO** (Camouflaged Objects)
- **COD10K** (10,000 camouflaged images)
- **NC4K** (Night camouflage)
- **Custom Odisha Dataset** (biodiversity images)

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/detect` | Upload image and get camouflage mask |
| `POST` | `/api/describe` | Get Claude Vision species description |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/ecosystems` | List Odisha ecosystem presets |

---

## 🗣️ Bilingual Output (English + Odia)

The system provides detection results in both English and Odia (ଓଡ଼ିଆ):

```json
{
  "en": "Rusty-spotted cat detected near mangrove roots (87% confidence)",
  "or": "ମ୍ୟାଙ୍ଗ୍ରୋଭ୍ ଶିଖରରେ ଜଙ୍ଗଲ ବିଲେଇ ଦେଖାଗଲା (87% ନିଶ୍ଚିତତା)"
}
```

---

## 🔬 Innovation Highlights

1. **Novel CCSIM Module** — Cross-scale feature alignment via channel similarity matrices
2. **SGFL with Boundary Emphasis** — Semantic guidance suppresses background textures mimicked by camouflage
3. **Odisha-Specific Training** — Fine-tuned on regional flora/fauna characteristics
4. **Edge Deployment Ready** — ONNX export for field tablets/phones
5. **Claude Vision Integration** — Contextual species identification and ecological notes
6. **Cloud-First Training** — Free GPU training via Google Colab & Kaggle

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- Odisha Forest Department
- Chilika Development Authority
- Wildlife Institute of India
- CAMO & COD10K dataset creators
