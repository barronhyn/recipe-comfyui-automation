"""Layout specs for each slide template."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .models import SlideTemplate

# Colour type alias
RGBA = Tuple[int, int, int, int]
RGB = Tuple[int, int, int]


@dataclass
class TextBlock:
    x: int
    y: int
    max_width: int
    font_size: int
    color: RGB = (255, 255, 255)
    bold: bool = False
    line_spacing: int = 8
    align: str = "left"  # left | center


@dataclass
class OverlaySpec:
    """Gradient/colour overlay applied on top of the background image."""
    # Vertical gradient: start_y=0 means top of image
    gradient_start_y: int = 0
    gradient_end_y: int = 1920
    start_alpha: int = 0    # 0=transparent
    end_alpha: int = 200    # 0-255


@dataclass
class SlideLayout:
    template: SlideTemplate
    overlay: OverlaySpec
    title_block: TextBlock
    body_blocks: list[TextBlock] = field(default_factory=list)
    bg_color: RGB = (30, 30, 30)  # used for template_only slides


# ── COVER ──────────────────────────────────────────────────────────────────────
COVER_LAYOUT = SlideLayout(
    template=SlideTemplate.COVER,
    overlay=OverlaySpec(gradient_start_y=900, gradient_end_y=1920, start_alpha=0, end_alpha=220),
    title_block=TextBlock(x=60, y=1350, max_width=960, font_size=72, bold=True),
    body_blocks=[
        TextBlock(x=60, y=1490, max_width=960, font_size=40, color=(220, 220, 220)),
    ],
)

# ── INGREDIENTS ────────────────────────────────────────────────────────────────
INGREDIENTS_LAYOUT = SlideLayout(
    template=SlideTemplate.INGREDIENTS,
    overlay=OverlaySpec(gradient_start_y=0, gradient_end_y=400, start_alpha=180, end_alpha=0),
    title_block=TextBlock(x=60, y=60, max_width=960, font_size=64, bold=True),
    body_blocks=[
        TextBlock(x=60, y=200, max_width=960, font_size=38, color=(240, 240, 240), line_spacing=12),
    ],
)

# ── STEPS 1-2 ──────────────────────────────────────────────────────────────────
STEPS12_LAYOUT = SlideLayout(
    template=SlideTemplate.STEPS12,
    overlay=OverlaySpec(gradient_start_y=800, gradient_end_y=1920, start_alpha=0, end_alpha=230),
    title_block=TextBlock(x=60, y=860, max_width=960, font_size=60, bold=True),
    body_blocks=[
        TextBlock(x=60, y=980, max_width=960, font_size=36, color=(235, 235, 235), line_spacing=14),
    ],
)

# ── STEPS 3-4 ──────────────────────────────────────────────────────────────────
STEPS34_LAYOUT = SlideLayout(
    template=SlideTemplate.STEPS34,
    overlay=OverlaySpec(gradient_start_y=800, gradient_end_y=1920, start_alpha=0, end_alpha=230),
    title_block=TextBlock(x=60, y=860, max_width=960, font_size=60, bold=True),
    body_blocks=[
        TextBlock(x=60, y=980, max_width=960, font_size=36, color=(235, 235, 235), line_spacing=14),
    ],
)

# ── NUTRITION (pure Pillow) ─────────────────────────────────────────────────────
NUTRITION_LAYOUT = SlideLayout(
    template=SlideTemplate.NUTRITION,
    overlay=OverlaySpec(start_alpha=0, end_alpha=0),  # no image overlay
    title_block=TextBlock(x=60, y=80, max_width=960, font_size=68, bold=True, color=(50, 50, 50)),
    body_blocks=[
        TextBlock(x=60, y=280, max_width=960, font_size=44, color=(70, 70, 70), line_spacing=20),
    ],
    bg_color=(250, 245, 235),
)

# ── CTA (pure Pillow) ──────────────────────────────────────────────────────────
CTA_LAYOUT = SlideLayout(
    template=SlideTemplate.CTA,
    overlay=OverlaySpec(start_alpha=0, end_alpha=0),
    title_block=TextBlock(x=60, y=700, max_width=960, font_size=72, bold=True, color=(255, 255, 255), align="center"),
    body_blocks=[
        TextBlock(x=60, y=850, max_width=960, font_size=44, color=(255, 230, 210), line_spacing=16, align="center"),
    ],
    bg_color=(255, 107, 53),  # brand orange
)


LAYOUTS: dict[SlideTemplate, SlideLayout] = {
    SlideTemplate.COVER: COVER_LAYOUT,
    SlideTemplate.INGREDIENTS: INGREDIENTS_LAYOUT,
    SlideTemplate.STEPS12: STEPS12_LAYOUT,
    SlideTemplate.STEPS34: STEPS34_LAYOUT,
    SlideTemplate.NUTRITION: NUTRITION_LAYOUT,
    SlideTemplate.CTA: CTA_LAYOUT,
}


def get_layout(template: SlideTemplate) -> SlideLayout:
    return LAYOUTS[template]
