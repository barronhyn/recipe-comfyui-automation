"""Unit tests for prompt generator."""
import os
os.environ.setdefault("MOCK_MODE", "true")

from src.mock_llm import SAMPLE_RECIPE
from src.prompt_generator import generate_slide_prompts


def test_returns_4_prompts():
    prompts = generate_slide_prompts(SAMPLE_RECIPE)
    assert len(prompts) == 4


def test_prompts_are_strings():
    prompts = generate_slide_prompts(SAMPLE_RECIPE)
    for p in prompts:
        assert isinstance(p, str) and len(p) > 20


def test_title_in_cover_prompt():
    prompts = generate_slide_prompts(SAMPLE_RECIPE)
    assert SAMPLE_RECIPE.title.lower() in prompts[0].lower()
