"""Main pipeline: input → 6 TikTok carousel slides."""
from __future__ import annotations

import base64
import logging
from typing import Optional

from . import config
from .llm_analyzer import analyze_food_image, generate_recipe_from_text
from .slide_planner import plan_slides
from .image_generator import generate_slide_images
from .slide_composer import compose_all_slides
from .models import CarouselOutput, SlideOutput, BrandConfig, PipelineInput

log = logging.getLogger(__name__)


class RecipePipeline:
    def __init__(
        self,
        brand: Optional[BrandConfig] = None,
    ) -> None:
        self.brand = brand or BrandConfig()

    def run(
        self,
        input_image: Optional[bytes] = None,
        input_text: Optional[str] = None,
    ) -> CarouselOutput:
        """
        Run the full pipeline.

        Provide input_image (JPEG/PNG bytes) OR input_text (recipe description).
        Returns CarouselOutput with 6 base64-encoded PNG slides.
        """
        if input_image is None and input_text is None:
            raise ValueError("Provide either input_image or input_text")

        # ── Step 1: Analyze input ──────────────────────────────────────────────
        if input_image is not None:
            log.info("Pipeline: analyzing food image")
            recipe = analyze_food_image(input_image)
        else:
            log.info("Pipeline: generating recipe from text: %s", input_text)
            recipe = generate_recipe_from_text(input_text)  # type: ignore[arg-type]

        # ── Step 2: Plan slides ────────────────────────────────────────────────
        has_user_image = input_image is not None
        specs = plan_slides(recipe, has_user_image=has_user_image)
        log.info("Planned %d slides", len(specs))

        # ── Step 3: Generate images (slides 1-4 via ComfyUI) ──────────────────
        images = generate_slide_images(specs, user_image=input_image)
        log.info("Generated %d images", len(images))

        # ── Step 4: Compose final slides (Pillow) ─────────────────────────────
        png_list = compose_all_slides(
            specs,
            images,
            brand_color=self.brand.color,
            brand_handle=self.brand.handle,
        )

        # ── Step 5: Build output ───────────────────────────────────────────────
        slide_names = [
            "slide_1_cover.png",
            "slide_2_ingredients.png",
            "slide_3_steps12.png",
            "slide_4_steps34.png",
            "slide_5_nutrition.png",
            "slide_6_cta.png",
        ]
        slides = [
            SlideOutput(name=name, data=base64.b64encode(png).decode())
            for name, png in zip(slide_names, png_list)
        ]

        return CarouselOutput(slides=slides, recipe=recipe, total_slides=6)


def run_from_api_input(payload: dict) -> dict:
    """Convenience wrapper for RunPod handler."""
    inp = PipelineInput(**payload)
    brand = inp.brand

    image_bytes: Optional[bytes] = None
    if inp.image:
        image_bytes = base64.b64decode(inp.image)

    pipeline = RecipePipeline(brand=brand)
    output = pipeline.run(input_image=image_bytes, input_text=inp.text)
    return output.model_dump()
