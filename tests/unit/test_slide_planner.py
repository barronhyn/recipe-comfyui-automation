"""Unit tests for slide planner."""
import os
os.environ.setdefault("MOCK_MODE", "true")

from src.mock_llm import SAMPLE_RECIPE
from src.slide_planner import plan_slides
from src.models import SlideType, SlideTemplate


def test_returns_6_slides():
    specs = plan_slides(SAMPLE_RECIPE)
    assert len(specs) == 6


def test_indices_are_1_to_6():
    specs = plan_slides(SAMPLE_RECIPE)
    assert [s.index for s in specs] == [1, 2, 3, 4, 5, 6]


def test_slides_5_6_are_template_only():
    specs = plan_slides(SAMPLE_RECIPE)
    by_idx = {s.index: s for s in specs}
    assert by_idx[5].slide_type == SlideType.TEMPLATE_ONLY
    assert by_idx[6].slide_type == SlideType.TEMPLATE_ONLY


def test_slide_1_ai_when_no_image():
    specs = plan_slides(SAMPLE_RECIPE, has_user_image=False)
    assert specs[0].slide_type == SlideType.AI_GENERATE


def test_slide_1_user_photo_when_image_provided():
    specs = plan_slides(SAMPLE_RECIPE, has_user_image=True)
    assert specs[0].slide_type == SlideType.USER_PHOTO


def test_slides_2_4_use_ip_adapter():
    specs = plan_slides(SAMPLE_RECIPE)
    by_idx = {s.index: s for s in specs}
    for i in (2, 3, 4):
        assert by_idx[i].use_ip_adapter is True


def test_templates_correct():
    specs = plan_slides(SAMPLE_RECIPE)
    expected = [
        SlideTemplate.COVER,
        SlideTemplate.INGREDIENTS,
        SlideTemplate.STEPS12,
        SlideTemplate.STEPS34,
        SlideTemplate.NUTRITION,
        SlideTemplate.CTA,
    ]
    for spec, tmpl in zip(specs, expected):
        assert spec.template == tmpl
