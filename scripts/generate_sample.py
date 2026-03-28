#!/usr/bin/env python3
"""
Quick local test: run the pipeline in MOCK_MODE and save 6 slides to ./output/.

Usage:
    MOCK_MODE=true python scripts/generate_sample.py
    MOCK_MODE=true python scripts/generate_sample.py --text "avocado toast"
    MOCK_MODE=true python scripts/generate_sample.py --image path/to/food.jpg
"""
import argparse
import base64
import os
import sys
from pathlib import Path

# Ensure src is importable from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("MOCK_MODE", "true")

from src.pipeline import RecipePipeline
from src.models import BrandConfig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="creamy garlic pasta", help="Recipe text prompt")
    parser.add_argument("--image", default=None, help="Path to food image")
    parser.add_argument("--out", default="output", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    image_bytes = None
    if args.image:
        with open(args.image, "rb") as f:
            image_bytes = f.read()

    pipeline = RecipePipeline(brand=BrandConfig())
    print(f"Running pipeline (MOCK_MODE={os.environ.get('MOCK_MODE', 'true')})...")
    output = pipeline.run(input_text=args.text if image_bytes is None else None, input_image=image_bytes)

    print(f"\nRecipe: {output.recipe.title}")
    print(f"Calories: {output.recipe.nutrition.calories} kcal")
    print(f"\nSaving {len(output.slides)} slides to ./{args.out}/")

    for slide in output.slides:
        path = out_dir / slide.name
        path.write_bytes(base64.b64decode(slide.data))
        print(f"  ✓ {slide.name}")

    print("\nDone!")


if __name__ == "__main__":
    main()
