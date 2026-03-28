"""Compose final slides: background image + gradient overlay + text."""
from __future__ import annotations

import io
import logging
from typing import Optional

from PIL import Image, ImageDraw

from . import config
from .models import SlideSpec, SlideTemplate, SlideType
from .template_engine import get_layout, SlideLayout
from .text_renderer import draw_text_block, draw_handle_badge

log = logging.getLogger(__name__)

_W = config.SLIDE_WIDTH
_H = config.SLIDE_HEIGHT


def _gradient_overlay(img: Image.Image, layout: SlideLayout) -> None:
    """Apply vertical dark gradient overlay in-place."""
    ov = layout.overlay
    if ov.start_alpha == 0 and ov.end_alpha == 0:
        return

    overlay = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    y_start = ov.gradient_start_y
    y_end = ov.gradient_end_y
    span = max(y_end - y_start, 1)

    for y in range(y_start, min(y_end + 1, _H)):
        t = (y - y_start) / span
        alpha = int(ov.start_alpha + t * (ov.end_alpha - ov.start_alpha))
        alpha = max(0, min(255, alpha))
        draw.line([(0, y), (_W, y)], fill=(0, 0, 0, alpha))

    img.paste(overlay, mask=overlay.split()[3])


def _open_bg(image_bytes: Optional[bytes], bg_color: tuple) -> Image.Image:
    if image_bytes:
        bg = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        bg = bg.resize((_W, _H), Image.LANCZOS)
    else:
        bg = Image.new("RGBA", (_W, _H), (*bg_color, 255))
    return bg


def compose_slide(
    spec: SlideSpec,
    bg_image: Optional[bytes],
    brand_color: str = config.BRAND_COLOR,
    brand_handle: str = config.BRAND_HANDLE,
) -> bytes:
    """Compose one slide and return PNG bytes."""
    layout = get_layout(spec.template)

    bg = _open_bg(bg_image, layout.bg_color)
    _gradient_overlay(bg, layout)

    draw = ImageDraw.Draw(bg)

    # Title
    if spec.title_text:
        draw_text_block(draw, layout.title_block, [spec.title_text])

    # Body
    if spec.body_lines and layout.body_blocks:
        body_block = layout.body_blocks[0]
        draw_text_block(draw, body_block, spec.body_lines)

    # Brand handle badge on all slides
    draw_handle_badge(bg, brand_handle, brand_color)

    buf = io.BytesIO()
    bg.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def compose_all_slides(
    specs: list[SlideSpec],
    images: dict[int, bytes],
    brand_color: str = config.BRAND_COLOR,
    brand_handle: str = config.BRAND_HANDLE,
) -> list[bytes]:
    """Return list of 6 PNG bytes in slide order."""
    results = []
    for spec in sorted(specs, key=lambda s: s.index):
        bg = images.get(spec.index)
        log.info("Composing slide %d (%s)", spec.index, spec.template)
        png = compose_slide(spec, bg, brand_color, brand_handle)
        results.append(png)
    return results
