#!/usr/bin/env python3
"""
Test the RunPod serverless endpoint.

Usage:
    RUNPOD_ENDPOINT_ID=abc123 RUNPOD_API_KEY=xxx python scripts/test_endpoint.py
    python scripts/test_endpoint.py --text "avocado toast" --endpoint-id abc123
"""
import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

RUNPOD_BASE = "https://api.runpod.ai/v2"


def submit_job(endpoint_id: str, api_key: str, payload: dict) -> str:
    url = f"{RUNPOD_BASE}/{endpoint_id}/run"
    resp = requests.post(
        url,
        json={"input": payload},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def poll_job(endpoint_id: str, api_key: str, job_id: str, timeout: int = 300) -> dict:
    url = f"{RUNPOD_BASE}/{endpoint_id}/status/{job_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        print(f"  Status: {status}")
        if status == "COMPLETED":
            return data.get("output", {})
        if status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Job {job_id} {status}: {data}")
        time.sleep(5)
    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="creamy garlic pasta")
    parser.add_argument("--endpoint-id", default=os.environ.get("RUNPOD_ENDPOINT_ID", ""))
    parser.add_argument("--api-key", default=os.environ.get("RUNPOD_API_KEY", ""))
    parser.add_argument("--out", default="output_runpod")
    args = parser.parse_args()

    if not args.endpoint_id or not args.api_key:
        print("ERROR: Set RUNPOD_ENDPOINT_ID and RUNPOD_API_KEY (or --endpoint-id / --api-key)")
        sys.exit(1)

    payload = {
        "content_type": "recipe",
        "text": args.text,
        "brand": {"color": "#FF6B35", "handle": "@calmcaloriesrecipes"},
    }

    print(f"Submitting job to endpoint {args.endpoint_id}...")
    job_id = submit_job(args.endpoint_id, args.api_key, payload)
    print(f"Job ID: {job_id}")

    print("Polling for result...")
    result = poll_job(args.endpoint_id, args.api_key, job_id)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    slides = result.get("slides", [])
    print(f"\nSaving {len(slides)} slides to ./{args.out}/")
    for slide in slides:
        path = out_dir / slide["name"]
        path.write_bytes(base64.b64decode(slide["data"]))
        print(f"  ✓ {slide['name']}")

    recipe = result.get("recipe", {})
    print(f"\nRecipe: {recipe.get('title', 'Unknown')}")
    print(f"Calories: {recipe.get('nutrition', {}).get('calories', '?')} kcal")
    print("\nDone!")


if __name__ == "__main__":
    main()
