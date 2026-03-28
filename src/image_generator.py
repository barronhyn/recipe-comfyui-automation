"""Generate images for slides 1-4 via ComfyUI. Slides 5-6 skip this step."""
from __future__ import annotations

import logging
from typing import Optional

from .models import SlideSpec, SlideType
from . import comfyui_client

log = logging.getLogger(__name__)


def generate_slide_images(
    specs: list[SlideSpec],
    user_image: Optional[bytes] = None,
) -> dict[int, bytes]:
    """
    Returns mapping of slide_index → image bytes for slides that need imagery.
    Slides with TEMPLATE_ONLY are excluded (handled by slide_composer).
    """
    images: dict[int, bytes] = {}
    anchor_image: Optional[bytes] = None  # slide 1 output used as IP-Adapter ref

    for spec in specs:
        if spec.slide_type == SlideType.TEMPLATE_ONLY:
            continue  # slides 5-6

        if spec.slide_type == SlideType.USER_PHOTO:
            if user_image:
                log.info("Slide %d: using user-provided photo", spec.index)
                images[spec.index] = user_image
                anchor_image = user_image
            else:
                log.warning("Slide %d: user_photo requested but no image supplied; falling back to AI gen", spec.index)
                img = comfyui_client.generate(spec.prompt or "")
                images[spec.index] = img
                anchor_image = img
            continue

        # AI_GENERATE
        if spec.use_ip_adapter and anchor_image is not None:
            log.info("Slide %d: AI generate with IP-Adapter ref", spec.index)
            img = comfyui_client.generate_with_reference(
                prompt=spec.prompt or "",
                ref_image=anchor_image,
            )
        else:
            log.info("Slide %d: AI generate (no ref)", spec.index)
            img = comfyui_client.generate(spec.prompt or "")
            if spec.index == 1:
                anchor_image = img  # first AI slide becomes anchor

        images[spec.index] = img

    return images
