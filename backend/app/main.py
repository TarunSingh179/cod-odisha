"""
COD-Odisha Backend API
======================
FastAPI server for camouflaged object detection.
Runs in mock mode until a trained model checkpoint is loaded.
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import io
import base64
import numpy as np
from PIL import Image, ImageFilter

app = FastAPI(
    title="COD-Odisha API",
    description="Camouflaged Object Detection for Odisha Biodiversity",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Ecosystem metadata ──────────────────────────────────────────

ECOSYSTEM_DATA = {
    "default": {
        "species": "Camouflaged organism",
        "conservation_status": "Not assessed",
        "en": "A camouflaged organism was detected in the uploaded image. The object blends with its surroundings using color matching and pattern disruption.",
        "or": "ଅପଲୋଡ୍ ହୋଇଥିବା ଚିତ୍ରରେ ଏକ ଛଦ୍ମବେଶୀ ଜୀବ ଚିହ୍ନଟ ହୋଇଛି। ବସ୍ତୁଟି ରଙ୍ଗ ମେଳ ଏବଂ ପ୍ୟାଟର୍ନ ବ୍ୟବହାର କରି ଏହାର ପରିବେଶ ସହ ମିଶିଯାଏ।",
        "ecological_notes": "Camouflage is a key survival adaptation used across many taxa in Odisha's diverse ecosystems.",
    },
    "simlipal": {
        "species": "Panthera tigris (Bengal Tiger)",
        "conservation_status": "Endangered",
        "en": "Potential tiger or large mammal detected in Simlipal sal forest habitat. The animal's striped coat provides excellent camouflage among dry leaves and dappled sunlight.",
        "or": "ସିମିଳିପାଳ ଶାଳ ଜଙ୍ଗଲରେ ଏକ ବାଘ ବା ବଡ଼ ସ୍ତନ୍ୟପାୟୀ ଚିହ୍ନଟ ହୋଇଛି। ଏହାର ଡୋରା ଚର୍ମ ଶୁଖିଲା ପତ୍ର ଓ ସୂର୍ଯ୍ୟ କିରଣ ମଧ୍ୟରେ ଉତ୍ତମ ଛଦ୍ମବେଶ ପ୍ରଦାନ କରେ।",
        "ecological_notes": "Simlipal Tiger Reserve is home to ~16 tigers. Their camouflage is vital for ambush predation in the dense sal forests of northern Odisha.",
    },
    "chilika": {
        "species": "Aquatic species (Chilika Lake)",
        "conservation_status": "Vulnerable habitat",
        "en": "Aquatic or avian species detected in Chilika Lake wetland. The organism uses counter-shading and color matching to blend with the brackish water environment.",
        "or": "ଚିଲିକା ହ୍ରଦ ଜଳାଭୂମିରେ ଜଳଚର ବା ପକ୍ଷୀ ପ୍ରଜାତି ଚିହ୍ନଟ ହୋଇଛି। ଜୀବଟି ଖାରା ପାଣି ପରିବେଶ ସହ ମିଶିବା ପାଇଁ ରଙ୍ଗ ମେଳ ବ୍ୟବହାର କରେ।",
        "ecological_notes": "Chilika is Asia's largest brackish water lagoon, hosting 160+ bird species including Irrawaddy dolphins.",
    },
    "paddy": {
        "species": "Agricultural pest species",
        "conservation_status": "Least Concern",
        "en": "Camouflaged pest or beneficial insect detected in paddy field. Early detection of pests like brown planthopper helps prevent crop damage across Odisha's rice belt.",
        "or": "ଧାନ କ୍ଷେତରେ ଛଦ୍ମବେଶୀ କୀଟ ବା ଉପକାରୀ ପୋକ ଚିହ୍ନଟ ହୋଇଛି। ବାଦାମୀ ଗଛ ଫୁଦି ପରି କୀଟଙ୍କ ଶୀଘ୍ର ଚିହ୍ନଟ ଫସଲ କ୍ଷତି ରୋକିବାରେ ସାହାଯ୍ୟ କରେ।",
        "ecological_notes": "Odisha's 4.18M hectares of paddy fields face annual pest damage. Computer vision-based detection enables precision agriculture.",
    },
    "bhitarkanika": {
        "species": "Crocodylus porosus (Saltwater Crocodile)",
        "conservation_status": "Least Concern (locally significant)",
        "en": "Reptile or mangrove-dwelling species detected in Bhitarkanika. Saltwater crocodiles blend seamlessly into muddy creek banks and mangrove roots.",
        "or": "ଭିତରକନିକାରେ ସରୀସୃପ ବା ମ୍ୟାନଗ୍ରୋଭ ପ୍ରଜାତି ଚିହ୍ନଟ ହୋଇଛି। ଲୁଣା ପାଣି କୁମ୍ଭୀର କାଦୁଆ ନାଳ କୂଳ ଓ ମ୍ୟାନଗ୍ରୋଭ ମୂଳ ସହ ସହଜରେ ମିଶିଯାଏ।",
        "ecological_notes": "Bhitarkanika hosts India's largest population of saltwater crocodiles (~1,800). Their cryptic behaviour makes monitoring challenging.",
    },
    "kandhamal": {
        "species": "Forest species (Kandhamal)",
        "conservation_status": "Data Deficient",
        "en": "Forest-dwelling organism detected in Kandhamal tropical deciduous habitat. The dense canopy and leaf litter provide ideal conditions for cryptic species.",
        "or": "କନ୍ଧମାଳ ଉଷ୍ଣମଣ୍ଡଳ ପର୍ଣ୍ଣପାତୀ ଜଙ୍ଗଲରେ ବନ୍ୟ ଜୀବ ଚିହ୍ନଟ ହୋଇଛି। ଘନ ଛାତ ଓ ପତ୍ର ସ୍ତର ଛଦ୍ମବେଶୀ ପ୍ରଜାତିଙ୍କ ପାଇଁ ଆଦର୍ଶ ପରିସ୍ଥିତି ପ୍ରଦାନ କରେ।",
        "ecological_notes": "Kandhamal's forests are part of the Eastern Ghats biodiversity hotspot with many endemic and elusive species.",
    },
}


# ── Request/Response models ─────────────────────────────────────

class DescribeRequest(BaseModel):
    ecosystem: str = "default"
    confidence: float = 0.0
    mask_area_pct: float = 0.0


# ── Helper: generate mock detection mask ─────────────────────────

def _generate_mock_images(uploaded_bytes: bytes) -> Dict[str, str]:
    """
    Create realistic-looking overlay / mask / heatmap from the uploaded
    image so the frontend has something useful to display.
    """
    img = Image.open(io.BytesIO(uploaded_bytes)).convert("RGB")
    w, h = img.size

    # --- mask: a simple elliptical region ---
    mask_np = np.zeros((h, w), dtype=np.uint8)
    cy, cx = h // 2, w // 2
    ry, rx = h // 4, w // 4
    yy, xx = np.ogrid[:h, :w]
    ellipse = ((yy - cy) ** 2 / (ry ** 2 + 1e-6) + (xx - cx) ** 2 / (rx ** 2 + 1e-6)) <= 1.0
    mask_np[ellipse] = 255
    mask_img = Image.fromarray(mask_np, mode="L")

    # --- heatmap: gaussian-blurred version of mask ---
    heatmap_img = mask_img.filter(ImageFilter.GaussianBlur(radius=max(w, h) // 8))
    heatmap_rgb = Image.merge("RGB", (
        heatmap_img,
        Image.fromarray(np.zeros_like(np.array(heatmap_img))),
        Image.fromarray(255 - np.array(heatmap_img)),
    ))

    # --- overlay: original image with red tint on detected region ---
    overlay = img.copy()
    overlay_np = np.array(overlay).copy()
    red_tint = overlay_np.copy()
    red_tint[:, :, 0] = np.clip(red_tint[:, :, 0].astype(int) + 80, 0, 255)
    red_tint[:, :, 1] = (red_tint[:, :, 1] * 0.6).astype(np.uint8)
    red_tint[:, :, 2] = (red_tint[:, :, 2] * 0.6).astype(np.uint8)
    mask_bool = mask_np > 0
    overlay_np[mask_bool] = red_tint[mask_bool]
    overlay_img = Image.fromarray(overlay_np)

    def _to_b64(pil_img: Image.Image) -> str:
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    return {
        "overlay": _to_b64(overlay_img),
        "mask": _to_b64(mask_img.convert("RGB")),
        "heatmap": _to_b64(heatmap_rgb),
    }


# ── Endpoints ────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "model_loaded": False,
        "mode": "mock -- model is training on Kaggle",
    }


@app.get("/api/ecosystems")
async def get_ecosystems() -> List[Dict[str, Any]]:
    return [
        {"id": "default",       "name": "General",       "description": "General purpose detection"},
        {"id": "simlipal",      "name": "Simlipal",      "description": "Wildlife in sal forests"},
        {"id": "chilika",       "name": "Chilika Lake",  "description": "Aquatic species & birds"},
        {"id": "paddy",         "name": "Paddy Fields",  "description": "Agricultural pest detection"},
        {"id": "bhitarkanika",  "name": "Bhitarkanika",  "description": "Mangrove ecosystem"},
        {"id": "kandhamal",     "name": "Kandhamal",     "description": "Tropical deciduous forest"},
    ]


@app.post("/api/detect")
async def detect_image(
    file: UploadFile = File(...),
    ecosystem: str = Form("default"),
) -> Dict[str, Any]:
    """
    Run camouflaged-object detection on the uploaded image.
    Currently returns mock results while model trains on Kaggle.
    """
    contents = await file.read()
    time.sleep(0.8)  # simulate inference latency

    images = _generate_mock_images(contents)
    mask_area_pct = 12.4  # mock value

    return {
        "success": True,
        "confidence": 0.88,
        "images": images,
        "detection": {
            "mask_area_pct": mask_area_pct,
            "has_detection": True,
        },
        "labels": ["camouflaged_object"],
    }


@app.post("/api/describe")
async def describe_species(req: DescribeRequest) -> Dict[str, Any]:
    """
    Return bilingual species description based on ecosystem context.
    """
    eco = ECOSYSTEM_DATA.get(req.ecosystem, ECOSYSTEM_DATA["default"])
    return {
        "en": eco["en"],
        "or": eco["or"],
        "species": eco["species"],
        "conservation_status": eco["conservation_status"],
        "ecological_notes": eco["ecological_notes"],
    }


# ── Run directly ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
