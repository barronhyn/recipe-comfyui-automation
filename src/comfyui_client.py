"""Real ComfyUI API client: queues prompts and retrieves generated images."""
from __future__ import annotations

import json
import logging
import os
import random
import time
import uuid
from pathlib import Path
from typing import Optional

import requests
import websocket

from . import config

log = logging.getLogger(__name__)

_WORKFLOW_IMAGE_GEN = Path(config.WORKFLOWS_DIR) / "image_gen.json"
_WORKFLOW_IPADAPTER = Path(config.WORKFLOWS_DIR) / "carousel_6slides_ipadapter.json"


def _load_workflow(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _inject_params(workflow: dict, prompt: str, seed: int, width: int, height: int) -> dict:
    wf = json.loads(json.dumps(workflow))  # deep copy
    wf["6"]["inputs"]["text"] = prompt
    wf["25"]["inputs"]["noise_seed"] = seed
    wf["27"]["inputs"]["width"] = width
    wf["27"]["inputs"]["height"] = height
    return wf


def _queue_prompt(workflow: dict, client_id: str) -> str:
    payload = {"prompt": workflow, "client_id": client_id}
    resp = requests.post(f"{config.COMFYUI_URL}/prompt", json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["prompt_id"]


def _wait_for_completion(prompt_id: str, client_id: str) -> None:
    ws_url = config.COMFYUI_URL.replace("http://", "ws://").replace("https://", "wss://")
    ws = websocket.create_connection(
        f"{ws_url}/ws?clientId={client_id}",
        timeout=config.COMFYUI_TIMEOUT,
    )
    try:
        deadline = time.time() + config.COMFYUI_TIMEOUT
        while time.time() < deadline:
            msg = json.loads(ws.recv())
            if msg.get("type") == "executing":
                data = msg.get("data", {})
                if data.get("node") is None and data.get("prompt_id") == prompt_id:
                    return  # done
    finally:
        ws.close()
    raise TimeoutError(f"ComfyUI did not finish prompt {prompt_id} in time")


def _fetch_image(prompt_id: str) -> bytes:
    history = requests.get(
        f"{config.COMFYUI_URL}/history/{prompt_id}", timeout=30
    ).json()
    outputs = history[prompt_id]["outputs"]
    # Find first image in outputs
    for node_output in outputs.values():
        for img in node_output.get("images", []):
            params = {"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img["type"]}
            resp = requests.get(f"{config.COMFYUI_URL}/view", params=params, timeout=30)
            resp.raise_for_status()
            return resp.content
    raise RuntimeError("No image found in ComfyUI output")


def generate(
    prompt: str,
    width: int = config.SLIDE_WIDTH,
    height: int = config.SLIDE_HEIGHT,
    seed: Optional[int] = None,
) -> bytes:
    if config.MOCK_MODE:
        from .mock_comfyui import mock_generate
        return mock_generate(prompt, seed)

    seed = seed if seed is not None else random.randint(0, 2**53)
    client_id = str(uuid.uuid4())
    workflow = _load_workflow(_WORKFLOW_IMAGE_GEN)
    workflow = _inject_params(workflow, prompt, seed, width, height)

    log.info("Queuing ComfyUI prompt (seed=%d)", seed)
    prompt_id = _queue_prompt(workflow, client_id)
    _wait_for_completion(prompt_id, client_id)
    return _fetch_image(prompt_id)


def generate_with_reference(
    prompt: str,
    ref_image: bytes,
    weight: float = config.IP_ADAPTER_WEIGHT,
    width: int = config.SLIDE_WIDTH,
    height: int = config.SLIDE_HEIGHT,
    seed: Optional[int] = None,
) -> bytes:
    """Use IP-Adapter workflow for style consistency. RunPod only."""
    if config.MOCK_MODE:
        from .mock_comfyui import mock_generate
        return mock_generate(prompt, seed)

    # On RunPod the ipadapter workflow must exist
    if not _WORKFLOW_IPADAPTER.exists():
        log.warning("IP-Adapter workflow not found, falling back to standard gen")
        return generate(prompt, width, height, seed)

    seed = seed if seed is not None else random.randint(0, 2**53)
    client_id = str(uuid.uuid4())
    workflow = _load_workflow(_WORKFLOW_IPADAPTER)
    workflow = _inject_params(workflow, prompt, seed, width, height)
    # Inject reference image via temp upload
    # (ComfyUI /upload/image endpoint)
    upload_resp = requests.post(
        f"{config.COMFYUI_URL}/upload/image",
        files={"image": ("ref.png", ref_image, "image/png")},
        timeout=30,
    )
    upload_resp.raise_for_status()
    ref_name = upload_resp.json()["name"]

    # Inject ref image into IP-Adapter nodes (201, 301, 401 per WORKFLOW_NOTES)
    for node_id in ("201", "301", "401"):
        if node_id in workflow:
            workflow[node_id]["inputs"]["image"] = ref_name
            workflow[node_id]["inputs"]["weight"] = weight

    log.info("Queuing ComfyUI IP-Adapter prompt (seed=%d)", seed)
    prompt_id = _queue_prompt(workflow, client_id)
    _wait_for_completion(prompt_id, client_id)
    return _fetch_image(prompt_id)
