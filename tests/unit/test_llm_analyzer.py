"""Unit tests for LLM analyzer (MOCK_MODE=true)."""
import os
import pytest

os.environ["MOCK_MODE"] = "true"

from src.llm_analyzer import analyze_food_image, generate_recipe_from_text
from src.models import RecipeData


def test_analyze_food_image_mock():
    recipe = analyze_food_image(b"fake_image_bytes")
    assert isinstance(recipe, RecipeData)
    assert len(recipe.steps) == 4
    assert recipe.nutrition.calories > 0


def test_generate_recipe_from_text_mock():
    recipe = generate_recipe_from_text("spaghetti carbonara")
    assert isinstance(recipe, RecipeData)
    assert "spaghetti carbonara" in recipe.title.lower() or len(recipe.title) > 0


def test_generate_recipe_empty_text():
    recipe = generate_recipe_from_text("")
    assert isinstance(recipe, RecipeData)
