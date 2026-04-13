# Recipe Carousel Automation

A pipeline that turns a **food image** or **text prompt** into **6 TikTok carousel slides** (1080×1920 PNG), powered by Claude Vision, ComfyUI (FLUX), and Pillow.

```
Input: "creamy garlic pasta"   →   6 recipe carousel slides
Input: [photo of a dish]       →   6 slides showing how to make it
```

---

## How It Works

```
┌─────────────────────────────────────────────┐
│  PYTHON (the brain)                         │
│                                             │
│  • Receive image or text input              │
│  • Claude Vision → analyze → RecipeData     │
│  • Generate 6 targeted image prompts        │
│  • Decide: ComfyUI gen vs. template only    │
│  • Call ComfyUI API × 4 (slides 1–4)        │
│  • Pillow: compose text overlays            │
│  • Output: 6 final PNG slides               │
└──────────────────┬──────────────────────────┘
                   │ HTTP API
┌──────────────────▼──────────────────────────┐
│  COMFYUI (the hands)                        │
│                                             │
│  • Receive: prompt + optional ref image     │
│  • FLUX Dev + IP-Adapter → 1080×1920 image  │
│  • Return: PNG bytes                        │
│  • No intelligence — pure image generation  │
└─────────────────────────────────────────────┘
```

---

## Content Modes

| Mode | Input | Output |
|------|-------|--------|
| **Recipe Creation** | Food image OR text prompt | 6 recipe tutorial slides |
| **Product Comparison** | 2 product images | 6 comparison infographic slides |

### Slide breakdown (Recipe mode)

| Slide | Content | Generator |
|-------|---------|-----------|
| 1 — Cover | Hero food photo | ComfyUI (or original photo) |
| 2 — Ingredients | Flat-lay ingredient shot | ComfyUI + IP-Adapter |
| 3 — Steps 1–2 | Cooking process photo | ComfyUI + IP-Adapter |
| 4 — Steps 3–4 | Cooking process photo | ComfyUI + IP-Adapter |
| 5 — Nutrition | Infographic card | Pillow only |
| 6 — CTA | Brand call-to-action card | Pillow only |

---

## Project Structure

```
recipe-comfyui-automation/
│
├── src/
│   ├── config.py               # Env config (MOCK_MODE, URLs, API keys)
│   ├── models.py               # Pydantic models: RecipeData, SlideSpec, CarouselOutput
│   │
│   ├── llm_analyzer.py         # Claude API: image → recipe, text → recipe
│   ├── prompt_generator.py     # RecipeData → 6 ComfyUI prompts
│   ├── slide_planner.py        # Decide: ai_generate vs user_photo vs template_only
│   │
│   ├── comfyui_client.py       # ComfyUI HTTP + WebSocket client
│   ├── image_generator.py      # Orchestrate ComfyUI calls per slide, handle IP-Adapter
│   │
│   ├── slide_composer.py       # Pillow: bg + gradient + text → final slide
│   ├── text_renderer.py        # Draw text, badges, nutrition charts
│   ├── template_engine.py      # Layout specs per slide type
│   │
│   ├── pipeline.py             # Main: input → 6 slides
│   ├── runpod_handler.py       # RunPod serverless entry point
│   │
│   ├── mock_llm.py             # Returns hardcoded recipe (no API call)
│   └── mock_comfyui.py         # Returns colored PNG (no GPU)
│
├── workflows/
│   ├── image_gen.json                  # Single image gen (API format, used by code)
│   ├── carousel_6slides_ui_v2.json     # 6-slide batch (UI format, for manual testing)
│   └── carousel_6slides_ipadapter.json # Production with IP-Adapter (API format)
│
├── tests/
│   ├── unit/                   # MOCK_MODE=true, no GPU, no API key needed
│   ├── integration/            # MOCK_MODE=false, real ComfyUI + Claude API
│   └── fixtures/               # sample_recipe.json, test images
│
├── scripts/
│   ├── generate_sample.py      # Quick local test — generates sample slides
│   └── test_endpoint.py        # Test deployed RunPod endpoint
│
├── docker/
│   └── Dockerfile              # RunPod serverless image
│
├── templates/fonts/            # .ttf font files for Pillow rendering
├── requirements.txt            # Local dependencies (no GPU)
└── requirements-gpu.txt        # RunPod dependencies (runpod SDK)
```

---

## Local Development (No GPU Required)

### Prerequisites

- Python 3.10+
- No GPU, no API key needed for local dev (`MOCK_MODE=true`)

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/recipe-comfyui-automation.git
cd recipe-comfyui-automation

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # or create manually:
echo "MOCK_MODE=true" > .env
```

### Run Unit Tests

```bash
pytest tests/unit/ -v
```

All unit tests run with mock LLM and mock ComfyUI — no external services required.

### Generate Sample Slides

```bash
python scripts/generate_sample.py
# Output: output/slide_1_cover.png ... slide_6_cta.png
```

---

## API Schema

### Request

```json
{
  "input": {
    "content_type": "recipe",
    "text": "creamy garlic pasta",
    "image": "<base64 encoded image, optional>",
    "brand": {
      "color": "#FF6B35",
      "handle": "@calmcaloriesrecipes"
    }
  }
}
```

> Provide either `text` or `image` (or both). If both are provided, the image takes priority.

### Response

```json
{
  "slides": [
    {"name": "slide_1_cover.png",       "data": "<base64>"},
    {"name": "slide_2_ingredients.png", "data": "<base64>"},
    {"name": "slide_3_steps12.png",     "data": "<base64>"},
    {"name": "slide_4_steps34.png",     "data": "<base64>"},
    {"name": "slide_5_nutrition.png",   "data": "<base64>"},
    {"name": "slide_6_cta.png",         "data": "<base64>"}
  ],
  "recipe": {
    "title": "Creamy Garlic Pasta",
    "calories": 450,
    "ingredients": ["..."],
    "steps": ["..."]
  },
  "total_slides": 6
}
```

---

## RunPod Deployment

### 1. Provision Infrastructure

In RunPod Console:

1. **Storage** → New Network Volume (50 GB)
2. **Pods** → Deploy pod with RTX 4090, attach the volume
3. SSH into the pod

### 2. Download Models

```bash
cd /workspace/ComfyUI/models

# FLUX Dev checkpoint (required for IP-Adapter)
cd checkpoints
wget -O flux1-dev-fp8.safetensors \
  "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8-e4m3fn.safetensors"

# VAE
cd ../vae
wget -O ae.safetensors \
  "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/ae.safetensors"

# CLIP text encoders
cd ../clip
wget -O clip_l.safetensors \
  "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
wget -O t5xxl_fp8_e4m3fn.safetensors \
  "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors"

# IP-Adapter (for visual consistency across slides 2–4)
mkdir -p ../ipadapter-flux && cd ../ipadapter-flux
wget -O ip-adapter.bin \
  "https://huggingface.co/Shakker-Labs/FLUX.1-dev-IP-Adapter/resolve/main/ip-adapter.bin"
```

### 3. Install IP-Adapter Custom Node

```bash
cd /workspace/ComfyUI/custom_nodes
git clone https://github.com/Shakker-Labs/ComfyUI-IPAdapter-Flux.git
cd ComfyUI-IPAdapter-Flux && pip install -r requirements.txt
```

### 4. Clone Repo & Run Integration Tests

```bash
cd /workspace
git clone https://github.com/YOUR_USERNAME/recipe-comfyui-automation.git
cd recipe-comfyui-automation
pip install -r requirements.txt -r requirements-gpu.txt

MOCK_MODE=false ANTHROPIC_API_KEY=sk-ant-xxx pytest tests/integration/ -v
```

### 5. Deploy as Serverless Endpoint

```bash
# Build and push Docker image (from local machine)
docker build -t YOUR_DOCKERHUB/recipe-comfyui:v1 \
  -f docker/Dockerfile --platform linux/amd64 .
docker push YOUR_DOCKERHUB/recipe-comfyui:v1

# RunPod Console: Serverless → New Endpoint → set image: YOUR_DOCKERHUB/recipe-comfyui:v1
```

### 6. Test the Endpoint

```bash
RUNPOD_ENDPOINT_ID=xxx RUNPOD_API_KEY=xxx python scripts/test_endpoint.py
```

---

## ComfyUI Workflow Details

The Python code dynamically injects parameters into `workflows/image_gen.json` before each API call:

| Node ID | Type | Field | Injected Value |
|---------|------|-------|----------------|
| `"6"` | CLIPTextEncode | `inputs.text` | Slide-specific prompt |
| `"25"` | RandomNoise | `inputs.noise_seed` | Random int per slide |
| `"27"` | EmptySD3LatentImage | `inputs.width/height` | Always 1080×1920 |

Fixed nodes (not modified per call):

| Node ID | Type | Value |
|---------|------|-------|
| `"10"` | VAELoader | ae.safetensors |
| `"11"` | DualCLIPLoader | clip_l + t5xxl_fp8 |
| `"12"` | UNETLoader | flux1-dev-fp8 |
| `"16"` | KSamplerSelect | euler |
| `"17"` | BasicScheduler | 20 steps |

For IP-Adapter (slides 2–4), use `carousel_6slides_ipadapter.json` which adds nodes `"15"`, `"201"`, `"301"`, `"401"` to apply the slide 1 image as a visual reference.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_MODE` | `true` | Skip real API/GPU calls (local dev) |
| `ANTHROPIC_API_KEY` | — | Required when `MOCK_MODE=false` |
| `COMFYUI_URL` | `http://127.0.0.1:8188` | ComfyUI server address |
| `COMFYUI_CLIENT_ID` | auto-generated | WebSocket client ID |
| `OUTPUT_DIR` | `output/` | Where slides are saved |

---

## Architecture Decisions

- **ComfyUI is stateless**: Python controls all logic. ComfyUI only generates images.
- **IP-Adapter for visual consistency**: Slides 2–4 reference slide 1 as anchor image, keeping color palette and lighting consistent across the carousel.
- **Slides 5–6 are pure Pillow**: Nutrition and CTA cards are programmatically composed — no AI generation needed.
- **Dependency injection**: `RecipePipeline` receives analyzer, generator, and composer as constructor arguments, making each component independently testable and swappable.
- **Modular for extension**: Architecture supports adding Product Comparison mode or other content verticals without modifying the core pipeline.

---

## Dependencies

```
pillow>=10.0.0          # Slide composition and text rendering
pydantic>=2.0.0         # Data models and validation
anthropic>=0.40.0       # Claude Vision API
websocket-client>=1.6.0 # ComfyUI WebSocket (job completion)
aiohttp>=3.9.0          # Async HTTP
requests>=2.31.0        # Sync HTTP
python-dotenv>=1.0.0    # .env loading
structlog>=23.0.0       # Structured logging
pytest>=7.0.0           # Testing
pytest-asyncio>=0.21.0  # Async test support
```

GPU (RunPod only):
```
runpod>=1.6.0           # Serverless handler
```
