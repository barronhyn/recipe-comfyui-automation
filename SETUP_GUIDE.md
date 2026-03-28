# SETUP GUIDE — Tất cả trong 1 file

## Bước 1: Test workflow trên comfyai.run (đã xong ✅)

Bạn đã test FLUX Schnell thành công. File `carousel_6slides_ui_v2.json` để test 6 ảnh batch.

## Bước 2: Init project + start Claude Agent

```bash
cd ~/recipe-comfyui-automation

# Copy docs vào project
cp CLAUDE.md WORKFLOW_NOTES.md ./
mkdir -p workflows
cp workflows/*.json ./workflows/

# Tạo .env
echo "MOCK_MODE=true" > .env
echo ".env" >> .gitignore

# Tạo folders
mkdir -p src tests/{unit,integration,fixtures} scripts templates/fonts docker

# Commit
git add -A && git commit -m "chore: init project" && git push

# Start Claude Agent
claude
```

Prompt đầu tiên:
```
Đọc CLAUDE.md và WORKFLOW_NOTES.md.
Code theo implementation plan Phase 1→7.
MOCK_MODE=true, không cần GPU hay API key.
Dùng "use context7" khi cần tra docs.
```

## Bước 3: RunPod (SAU khi code xong)

### Tạo Volume + Download Models
```
RunPod Console → Storage → + New Network Volume (50GB)
→ Deploy Pod (RTX 4090) → SSH vào → download models:
```

```bash
cd /workspace/ComfyUI/models/checkpoints
wget -O flux1-dev-fp8.safetensors \
  "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8-e4m3fn.safetensors"
cd ../vae && wget -O ae.safetensors "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/ae.safetensors"
cd ../clip && wget -O clip_l.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
wget -O t5xxl_fp8_e4m3fn.safetensors "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors"

# IP-Adapter
mkdir -p ../ipadapter-flux && cd ../ipadapter-flux
wget -O ip-adapter.bin "https://huggingface.co/Shakker-Labs/FLUX.1-dev-IP-Adapter/resolve/main/ip-adapter.bin"

# Custom node
cd /workspace/ComfyUI/custom_nodes
git clone https://github.com/Shakker-Labs/ComfyUI-IPAdapter-Flux.git
cd ComfyUI-IPAdapter-Flux && pip install -r requirements.txt
```

### Clone repo + Integration test
```bash
cd /workspace
git clone https://github.com/YOU/recipe-comfyui-automation.git
cd recipe-comfyui-automation
pip install -r requirements.txt -r requirements-gpu.txt
MOCK_MODE=false ANTHROPIC_API_KEY=xxx pytest tests/integration/ -v
```

### Deploy Serverless
```bash
# Local: build + push Docker
docker build -t YOU/recipe-comfyui:v1 -f docker/Dockerfile --platform linux/amd64 .
docker push YOU/recipe-comfyui:v1

# RunPod Console: Serverless → New Endpoint → image: YOU/recipe-comfyui:v1
```

## Budget ($20)
Volume $5/mo + Pod ~$3-4 + Serverless test ~$2 = ~$10. Buffer $10.
