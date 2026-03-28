"""Unit tests for Pydantic models."""
import json
import os
import pytest

os.environ.setdefault("MOCK_MODE", "true")

from src.models import RecipeData, NutritionInfo, SlideSpec, SlideType, SlideTemplate, CarouselOutput


FIXTURE = json.load(open("tests/fixtures/sample_recipe.json"))


def test_recipe_data_parses():
    recipe = RecipeData(**FIXTURE)
    assert recipe.title == "Creamy Garlic Pasta"
    assert len(recipe.steps) == 4
    assert recipe.nutrition.calories == 450


def test_recipe_data_requires_4_steps():
    bad = {**FIXTURE, "steps": ["only one step"]}
    with pytest.raises(Exception):
        RecipeData(**bad)


def test_slide_spec_defaults():
    spec = SlideSpec(
        index=1,
        slide_type=SlideType.AI_GENERATE,
        template=SlideTemplate.COVER,
    )
    assert spec.use_ip_adapter is False
    assert spec.body_lines == []


def test_carousel_output_total():
    from src.mock_llm import SAMPLE_RECIPE
    from src.models import SlideOutput, CarouselOutput
    slides = [SlideOutput(name=f"slide_{i}.png", data="abc") for i in range(1, 7)]
    out = CarouselOutput(slides=slides, recipe=SAMPLE_RECIPE)
    assert out.total_slides == 6
