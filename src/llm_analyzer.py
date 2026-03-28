"""LLM Analyzer: Claude Vision API → structured recipe/comparison data."""
from __future__ import annotations

import base64
import json
import logging
from typing import Optional

from . import config
from .models import RecipeData, NutritionInfo, ComparisonData

log = logging.getLogger(__name__)

_RECIPE_SCHEMA = {
    "title": "string",
    "description": "string (1 sentence)",
    "ingredients": ["list of strings"],
    "steps": ["exactly 4 strings — each a complete cooking step"],
    "nutrition": {
        "calories": "int",
        "protein_g": "float",
        "carbs_g": "float",
        "fat_g": "float",
        "fiber_g": "float",
    },
    "prep_time_min": "int",
    "cook_time_min": "int",
    "servings": "int",
}

_SYSTEM_PROMPT = (
    "You are a professional recipe analyst. Always respond with valid JSON only. "
    "No markdown, no explanation — pure JSON matching the requested schema."
)


def _client():
    import anthropic
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _parse_recipe(raw: str) -> RecipeData:
    data = json.loads(raw)
    nutrition = NutritionInfo(**data.pop("nutrition"))
    steps = data.get("steps", [])
    # Ensure exactly 4 steps
    while len(steps) < 4:
        steps.append("Continue cooking as needed.")
    data["steps"] = steps[:4]
    return RecipeData(nutrition=nutrition, **data)


def analyze_food_image(image_bytes: bytes) -> RecipeData:
    if config.MOCK_MODE:
        from .mock_llm import mock_analyze_food_image
        return mock_analyze_food_image(image_bytes)

    log.info("Analyzing food image via Claude Vision API")
    b64 = base64.standard_b64encode(image_bytes).decode()
    client = _client()
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Analyze this food image. Return JSON matching this schema:\n"
                            f"{json.dumps(_RECIPE_SCHEMA, indent=2)}"
                        ),
                    },
                ],
            }
        ],
    )
    return _parse_recipe(msg.content[0].text)


def generate_recipe_from_text(prompt: str) -> RecipeData:
    if config.MOCK_MODE:
        from .mock_llm import mock_generate_recipe_from_text
        return mock_generate_recipe_from_text(prompt)

    log.info("Generating recipe from text: %s", prompt)
    client = _client()
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate a complete recipe for: {prompt}\n"
                    f"Return JSON matching this schema:\n"
                    f"{json.dumps(_RECIPE_SCHEMA, indent=2)}"
                ),
            }
        ],
    )
    return _parse_recipe(msg.content[0].text)


def analyze_products(img_a: bytes, img_b: bytes) -> ComparisonData:
    if config.MOCK_MODE:
        from .mock_llm import mock_analyze_products
        return mock_analyze_products(img_a, img_b)

    log.info("Comparing two product images via Claude Vision API")
    schema = {
        "product_a_name": "string",
        "product_b_name": "string",
        "calories_a": "int",
        "calories_b": "int",
        "price_a": "float (USD)",
        "price_b": "float (USD)",
        "pros_a": ["list of 3 strings"],
        "cons_a": ["list of 3 strings"],
        "pros_b": ["list of 3 strings"],
        "cons_b": ["list of 3 strings"],
        "verdict": "string (1-2 sentences)",
    }

    def _img_block(data: bytes, idx: int) -> dict:
        b64 = base64.standard_b64encode(data).decode()
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
        }

    client = _client()
    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    _img_block(img_a, 0),
                    _img_block(img_b, 1),
                    {
                        "type": "text",
                        "text": (
                            "Compare these two products. First image is product A, second is product B. "
                            f"Return JSON matching this schema:\n{json.dumps(schema, indent=2)}"
                        ),
                    },
                ],
            }
        ],
    )
    data = json.loads(msg.content[0].text)
    return ComparisonData(**data)
