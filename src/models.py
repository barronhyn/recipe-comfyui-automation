from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class NutritionInfo(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float = 0.0


class RecipeData(BaseModel):
    title: str
    description: str = ""
    ingredients: List[str]
    steps: List[str] = Field(..., min_length=4, max_length=4, description="Exactly 4 cooking steps")
    nutrition: NutritionInfo
    prep_time_min: int = 15
    cook_time_min: int = 30
    servings: int = 2


class ComparisonData(BaseModel):
    product_a_name: str
    product_b_name: str
    calories_a: int
    calories_b: int
    price_a: float
    price_b: float
    pros_a: List[str]
    cons_a: List[str]
    pros_b: List[str]
    cons_b: List[str]
    verdict: str


class SlideType(str, Enum):
    AI_GENERATE = "ai_generate"
    USER_PHOTO = "user_photo"
    TEMPLATE_ONLY = "template_only"


class SlideTemplate(str, Enum):
    COVER = "cover"
    INGREDIENTS = "ingredients"
    STEPS12 = "steps12"
    STEPS34 = "steps34"
    NUTRITION = "nutrition"
    CTA = "cta"


class SlideSpec(BaseModel):
    index: int  # 1-6
    slide_type: SlideType
    template: SlideTemplate
    prompt: Optional[str] = None
    title_text: str = ""
    body_lines: List[str] = Field(default_factory=list)
    use_ip_adapter: bool = False


class SlideOutput(BaseModel):
    name: str
    data: str  # base64-encoded PNG


class CarouselOutput(BaseModel):
    slides: List[SlideOutput]
    recipe: RecipeData
    total_slides: int = 6


class BrandConfig(BaseModel):
    color: str = "#FF6B35"
    handle: str = "@calmcaloriesrecipes"


class PipelineInput(BaseModel):
    content_type: str = "recipe"
    image: Optional[str] = None  # base64
    text: Optional[str] = None
    brand: BrandConfig = Field(default_factory=BrandConfig)
