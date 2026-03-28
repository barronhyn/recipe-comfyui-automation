# CLAUDE.md — Recipe Carousel Automation (ComfyUI + RunPod)

## What We're Building

A pipeline that takes **1 input** (food image OR text prompt) and outputs **6 TikTok carousel slides** (1080×1920 PNG).

```
Input: "creamy garlic pasta"     →  6 slides showing the recipe
Input: [photo of a pasta dish]   →  6 slides showing how to make it
```

Two content modes:
1. **Recipe Creation** — quy trình nấu món
2. **Product Comparison** — so sánh 2 sản phẩm (needs 2 images input)

---

## Where Logic Lives

```
┌─────────────────────────────────────────────┐
│  PYTHON SRC CODE (the brain)                │
│                                             │
│  • Receive input (image or text)            │
│  • LLM Vision: analyze image → recipe data  │
│  • LLM: generate 6 specific prompts         │
│  • Decide: which slides use original image   │
│  • Call ComfyUI API 4x (slides 1-4)         │
│  • Pillow: compose text overlays             │
│  • Output: 6 final PNG slides               │
└──────────────────┬──────────────────────────┘
                   │ calls API
┌──────────────────▼──────────────────────────┐
│  COMFYUI WORKFLOW (the hands)               │
│                                             │
│  • Receive: prompt text + optional ref image │
│  • Generate: 1080×1920 image                │
│  • IP-Adapter: style consistency from ref    │
│  • Return: PNG image bytes                  │
│  • NO intelligence — just image generation  │
└─────────────────────────────────────────────┘
```

ComfyUI workflow stays simple (single image gen). Python code calls it multiple times with different prompts.

---

## Pipeline Flow (detailed)

### Case A: User provides food IMAGE

```
1. [Python] Send image to Claude Vision API
   → "Analyze this food image. Return: dish name, ingredients,
      4 cooking steps, nutrition estimate"
   → Returns: RecipeData (structured JSON)

2. [Python] Generate 6 slide prompts from RecipeData:
   Slide 1 prompt: "food photography of {title}, top-down, studio light"
   Slide 2 prompt: "flat lay of {ingredients} on marble, top-down"
   Slide 3 prompt: "cooking {step1}, kitchen, warm light, close-up"
   Slide 4 prompt: "cooking {step3}, kitchen, warm light"
   Slide 5: no image gen needed (Pillow creates nutrition infographic)
   Slide 6: no image gen needed (Pillow creates CTA card)

3. [Python → ComfyUI API] Generate slide 1 image (or use original photo)
4. [Python → ComfyUI API] Generate slides 2-4 with IP-Adapter ref slide 1
5. [Python + Pillow] Create slides 5-6 (pure text/infographic)
6. [Python + Pillow] Overlay text on all 6 slides (title, calories, steps)
7. Output: 6 PNG files
```

### Case B: User provides TEXT prompt

```
1. [Python] Send text to Claude API
   → "Generate a complete recipe for: {user_prompt}.
      Return: dish name, ingredients, 4 cooking steps, nutrition"
   → Returns: RecipeData (structured JSON)

2-7: Same as Case A, but slide 1 is always AI-generated (no original photo)
```

### Case C: Product Comparison (2 images)

```
1. [Python] Send both images to Claude Vision API
   → Compare products, extract nutrition, price, pros/cons
2. [Python + Pillow] Create 6 comparison slides (mostly text/infographic)
   → May use ComfyUI only for enhancing/resizing product images
```

---

## ⚠️ Development Workflow: Code Local → Push → Test on RunPod

```
LOCAL (MOCK_MODE=true)                 RUNPOD (MOCK_MODE=false)
─────────────────                      ──────────────────
Mock LLM returns sample recipe   →     Real Claude Vision API
Mock ComfyUI returns colored PNG →     Real FLUX image generation
Unit tests pass 100%             →     Integration tests
git push                         →     Debug/fix → git push
```

---

## Project Structure

```
recipe-comfyui-automation/
├── CLAUDE.md                          # This file
├── WORKFLOW_NOTES.md                  # ComfyUI node IDs
│
├── workflows/
│   ├── image_gen.json                 # Single image gen (API format, for code)
│   ├── carousel_6slides_ui_v2.json    # 6-slide batch (UI format, for manual test)
│   └── carousel_6slides_ipadapter.json # Production with IP-Adapter (API format)
│
├── src/
│   ├── config.py                      # Env config
│   ├── models.py                      # Pydantic: RecipeData, SlideSpec, etc.
│   │
│   ├── # --- Brain: LLM analysis + prompt generation ---
│   ├── llm_analyzer.py                # Claude API: image→recipe, text→recipe
│   ├── prompt_generator.py            # RecipeData → 6 slide prompts
│   ├── slide_planner.py               # Decide: which slides need AI gen vs template
│   │
│   ├── # --- Hands: image generation ---
│   ├── comfyui_client.py              # Real ComfyUI API client
│   ├── image_generator.py             # Call ComfyUI per slide, handle IP-Adapter
│   │
│   ├── # --- Assembly: text overlay + compositing ---
│   ├── slide_composer.py              # Pillow: bg image + text overlay → final slide
│   ├── text_renderer.py               # Draw text, badges, nutrition charts
│   ├── template_engine.py             # Layout specs per slide type
│   │
│   ├── # --- Orchestration ---
│   ├── pipeline.py                    # Main: input → 6 slides output
│   ├── runpod_handler.py              # RunPod serverless entry point
│   │
│   ├── # --- Mocks (for local testing) ---
│   ├── mock_llm.py                    # Returns sample recipe, no API call
│   └── mock_comfyui.py                # Returns colored PNG, no GPU
│
├── templates/fonts/                   # .ttf files
├── tests/unit/                        # MOCK_MODE=true, local
├── tests/integration/                 # MOCK_MODE=false, RunPod
├── tests/fixtures/                    # sample_recipe.json, sample images
├── scripts/
│   ├── generate_sample.py             # Quick local test
│   └── test_endpoint.py               # Test RunPod API
│
├── requirements.txt                   # Local (no GPU)
└── requirements-gpu.txt               # RunPod (runpod SDK)
```

---

## Implementation Plan

### Phase 1: Models + Config
```
src/models.py — RecipeData, SlideSpec, CarouselOutput (Pydantic v2)
src/config.py — MOCK_MODE, COMFYUI_URL, ANTHROPIC_API_KEY, etc.
```

### Phase 2: LLM Brain
```
src/llm_analyzer.py
  - analyze_food_image(image_bytes) → RecipeData
  - generate_recipe_from_text(prompt) → RecipeData
  - analyze_products(img_a, img_b) → ComparisonData
  Uses Anthropic SDK. Mock returns hardcoded sample data.

src/prompt_generator.py
  - generate_slide_prompts(recipe: RecipeData) → list[str]
  Returns 6 optimized SD prompts for food photography.

src/slide_planner.py
  - plan_slides(recipe, has_user_image) → list[SlideSpec]
  Decides per slide: ai_generate vs user_photo vs template_only
  Max 6 slides. Slides 5-6 always template_only.
```

### Phase 3: ComfyUI Client
```
src/comfyui_client.py
  - generate(prompt, width, height, seed) → bytes
  - generate_with_reference(prompt, ref_image, weight, ...) → bytes
  Loads workflow JSON, injects params, queues via API.

src/image_generator.py
  - generate_slide_images(specs, ref_image?) → list[bytes]
  Calls comfyui_client per slide. Handles IP-Adapter for slides 2-4.
```

### Phase 4: Slide Composition
```
src/slide_composer.py + text_renderer.py + template_engine.py
  Pure Pillow. Compose: background + gradient overlay + text + badges.
  All testable locally with mock images.
```

### Phase 5: Pipeline Orchestration
```
src/pipeline.py
  class RecipePipeline:
    async def run(self, input_image=None, input_text=None) → CarouselOutput:
      1. Analyze input → RecipeData
      2. Plan 6 slides
      3. Generate prompts
      4. Generate images (ComfyUI)
      5. Compose final slides (Pillow)
      6. Return 6 PNGs
```

### Phase 6: Tests
```
Unit tests: MOCK_MODE=true, no GPU, no API key
Integration: MOCK_MODE=false, real ComfyUI + Claude API on RunPod
```

### Phase 7: Docker + RunPod Handler
```
Dockerfile, runpod_handler.py, scripts/test_endpoint.py
```

---

## API Schema

### Request
```json
{
  "input": {
    "content_type": "recipe",
    "image": "<base64, optional — provide this OR text>",
    "text": "creamy garlic pasta",
    "brand": {"color": "#FF6B35", "handle": "@calmcaloriesrecipes"}
  }
}
```

### Response
```json
{
  "slides": [
    {"name": "slide_1_cover.png", "data": "<base64>"},
    {"name": "slide_2_ingredients.png", "data": "<base64>"},
    {"name": "slide_3_steps12.png", "data": "<base64>"},
    {"name": "slide_4_steps34.png", "data": "<base64>"},
    {"name": "slide_5_nutrition.png", "data": "<base64>"},
    {"name": "slide_6_cta.png", "data": "<base64>"}
  ],
  "recipe": {"title": "Creamy Garlic Pasta", "calories": 450, ...},
  "total_slides": 6
}
```

---

## Key Rules for Claude Agent

1. **ComfyUI = dumb image generator.** All intelligence is in Python.
2. **MOCK_MODE=true** for all local dev. Mock LLM + mock ComfyUI.
3. **Dependency injection** — pipeline receives analyzer + generator + composer.
4. **Max 6 slides**, always 1080×1920.
5. **Slides 5-6 are PURE Pillow** — no ComfyUI call needed.
6. **IP-Adapter only on RunPod** (FLUX Dev). Local mock skips it.
7. **use context7** for library docs.
8. **Text overlay in Pillow**, not ComfyUI text nodes.
9. **Conventional commits**, never commit .env.
10. Architecture must be **modular** — client will extend to product comparison and other verticals.

## Dependencies (requirements.txt)
```
pillow>=10.0.0
pydantic>=2.0.0
anthropic>=0.40.0
websocket-client>=1.6.0
aiohttp>=3.9.0
requests>=2.31.0
python-dotenv>=1.0.0
structlog>=23.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```
