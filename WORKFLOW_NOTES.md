# WORKFLOW_NOTES.md

## How Python code uses ComfyUI workflow

```
Python pipeline calls ComfyUI API like this:

Loop 4 times (slides 1-4):
  1. Load image_gen.json template
  2. Inject: prompt, seed, size into correct nodes
  3. POST /prompt → queue workflow
  4. Wait for result via WebSocket
  5. GET /view → download generated image
  6. Pass image to Pillow for text overlay

Slides 5-6: skip ComfyUI, Pillow creates directly
```

Python decides WHAT to generate. ComfyUI decides HOW to generate.

---

## Workflow: image_gen.json (API format — for Python code)

### Nodes to inject per call
| Node ID | Class | Field | What Python injects |
|---------|-------|-------|-------------------|
| `"6"` | CLIPTextEncode | `inputs.text` | Slide-specific prompt |
| `"25"` | RandomNoise | `inputs.noise_seed` | Random int per slide |
| `"27"` | EmptySD3LatentImage | `inputs.width/height` | Always 1080×1920 |

### Nodes that stay fixed
| Node ID | Class | Value |
|---------|-------|-------|
| `"10"` | VAELoader | ae.safetensors |
| `"11"` | DualCLIPLoader | clip_l + t5xxl_fp8 |
| `"12"` | UNETLoader | flux1-schnell-fp8 (or dev) |
| `"16"` | KSamplerSelect | euler |
| `"17"` | BasicScheduler | 4 steps (schnell) or 20 (dev) |

### Python pseudo-code for workflow_builder.py
```python
import json, random

def build_workflow(prompt: str, seed: int = None) -> dict:
    with open("workflows/image_gen.json") as f:
        wf = json.load(f)

    wf["6"]["inputs"]["text"] = prompt
    wf["25"]["inputs"]["noise_seed"] = seed or random.randint(0, 2**53)
    wf["27"]["inputs"]["width"] = 1080
    wf["27"]["inputs"]["height"] = 1920

    return wf
```

---

## Workflow: carousel_6slides_ipadapter.json (API format — production)

Same as image_gen.json but includes IP-Adapter for consistency.
Slide 1 generates anchor image → slides 2-4 reference it.

### Additional nodes (IP-Adapter slides only)
| Node ID | Class | Field |
|---------|-------|-------|
| `"15"` | IPAdapterFluxLoader | ip-adapter.bin |
| `"201/301/401"` | ApplyIPAdapterFlux | weight: 0.6-0.7, image ← slide 1 output |

### Required extra model
```bash
mkdir -p models/ipadapter-flux
wget -O models/ipadapter-flux/ip-adapter.bin \
  "https://huggingface.co/Shakker-Labs/FLUX.1-dev-IP-Adapter/resolve/main/ip-adapter.bin"
```

Requires FLUX Dev (not Schnell). Test on RunPod only.

---

## Workflow: carousel_6slides_ui_v2.json (UI format — manual testing)

For drag-and-drop into comfyai.run. Same logic as image_gen.json × 6.
57 nodes, 72 links, all verified programmatically.
Prompts hardcoded for "creamy garlic pasta" recipe.

---

## Prompt patterns (Python generates these per recipe)

```python
PROMPTS = {
    "cover": "professional food photography of {title}, top-down view, "
             "studio lighting, clean white plate, 4k, food magazine style",

    "ingredients": "flat lay of {ingredient_list} on white marble, "
                   "top-down, soft natural light, food styling, "
                   "clean composition with negative space for text",

    "cooking_step": "close-up of {step_description}, kitchen scene, "
                    "warm lighting, cooking process photography, "
                    "professional food content",

    "clean_bg": "soft minimal gradient background, warm beige to cream, "
                "clean, empty space for text overlay, minimal aesthetic",

    "brand_bg": "solid warm coral orange gradient, smooth clean minimal, "
                "no objects, empty space for branding text"
}
```

## Models download (RunPod)
```bash
# Schnell (test)
wget -O models/checkpoints/flux1-schnell-fp8.safetensors \
  "https://huggingface.co/Comfy-Org/flux1-schnell/resolve/main/flux1-schnell-fp8.safetensors"

# Dev (production, needed for IP-Adapter)
wget -O models/checkpoints/flux1-dev-fp8.safetensors \
  "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8-e4m3fn.safetensors"

# Shared
wget -O models/vae/ae.safetensors "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/ae.safetensors"
wget -O models/clip/clip_l.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
wget -O models/clip/t5xxl_fp8_e4m3fn.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors"
```
