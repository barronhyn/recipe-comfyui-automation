"""Unit tests for slide composer (pure Pillow, no GPU)."""
import io
import os
os.environ["MOCK_MODE"] = "true"

import pytest
from PIL import Image

from src.mock_llm import SAMPLE_RECIPE
from src.slide_planner import plan_slides
from src.slide_composer import compose_slide, compose_all_slides
from src import config


def _is_valid_png(data: bytes) -> bool:
    return data[:8] == b"\x89PNG\r\n\x1a\n"


def test_compose_slide_template_only():
    specs = plan_slides(SAMPLE_RECIPE)
    nutrition_spec = next(s for s in specs if s.index == 5)
    png = compose_slide(nutrition_spec, bg_image=None)
    assert _is_valid_png(png)
    img = Image.open(io.BytesIO(png))
    assert img.size == (config.SLIDE_WIDTH, config.SLIDE_HEIGHT)


def test_compose_slide_with_bg():
    from src.mock_comfyui import mock_generate
    specs = plan_slides(SAMPLE_RECIPE)
    cover_spec = specs[0]
    bg = mock_generate("test", slide_index=0)
    png = compose_slide(cover_spec, bg_image=bg)
    assert _is_valid_png(png)


def test_compose_all_returns_6():
    from src.mock_comfyui import mock_generate
    specs = plan_slides(SAMPLE_RECIPE)
    images = {
        1: mock_generate("cover", slide_index=0),
        2: mock_generate("ingredients", slide_index=1),
        3: mock_generate("steps12", slide_index=2),
        4: mock_generate("steps34", slide_index=3),
    }
    results = compose_all_slides(specs, images)
    assert len(results) == 6
    for png in results:
        assert _is_valid_png(png)
