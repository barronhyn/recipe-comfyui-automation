"""End-to-end pipeline test with MOCK_MODE=true."""
import base64
import io
import os
os.environ["MOCK_MODE"] = "true"

import pytest
from PIL import Image

from src.pipeline import RecipePipeline, run_from_api_input
from src.models import CarouselOutput, BrandConfig
from src import config


def test_pipeline_text_input():
    pipeline = RecipePipeline()
    output = pipeline.run(input_text="creamy garlic pasta")
    assert isinstance(output, CarouselOutput)
    assert output.total_slides == 6
    assert len(output.slides) == 6


def test_pipeline_slide_names():
    pipeline = RecipePipeline()
    output = pipeline.run(input_text="avocado toast")
    names = [s.name for s in output.slides]
    assert names == [
        "slide_1_cover.png",
        "slide_2_ingredients.png",
        "slide_3_steps12.png",
        "slide_4_steps34.png",
        "slide_5_nutrition.png",
        "slide_6_cta.png",
    ]


def test_pipeline_slides_are_valid_pngs():
    pipeline = RecipePipeline()
    output = pipeline.run(input_text="tacos")
    for slide in output.slides:
        data = base64.b64decode(slide.data)
        assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{slide.name} is not a valid PNG"


def test_pipeline_slide_dimensions():
    pipeline = RecipePipeline()
    output = pipeline.run(input_text="pasta")
    for slide in output.slides:
        data = base64.b64decode(slide.data)
        img = Image.open(io.BytesIO(data))
        assert img.size == (config.SLIDE_WIDTH, config.SLIDE_HEIGHT), (
            f"{slide.name} has wrong size: {img.size}"
        )


def test_pipeline_image_input():
    # Create a tiny fake JPEG
    img = Image.new("RGB", (100, 100), (200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    pipeline = RecipePipeline()
    output = pipeline.run(input_image=buf.getvalue())
    assert output.total_slides == 6


def test_pipeline_no_input_raises():
    pipeline = RecipePipeline()
    with pytest.raises(ValueError):
        pipeline.run()


def test_run_from_api_input():
    payload = {
        "content_type": "recipe",
        "text": "chicken stir fry",
        "brand": {"color": "#FF6B35", "handle": "@testrecipes"},
    }
    result = run_from_api_input(payload)
    assert "slides" in result
    assert len(result["slides"]) == 6


def test_brand_config_propagates():
    brand = BrandConfig(color="#123456", handle="@mybrand")
    pipeline = RecipePipeline(brand=brand)
    output = pipeline.run(input_text="test")
    assert output.total_slides == 6  # just ensure it runs; visual checks are manual
