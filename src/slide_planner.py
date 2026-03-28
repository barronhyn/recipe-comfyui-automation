"""Decide per-slide generation strategy: ai_generate vs user_photo vs template_only."""
from .models import RecipeData, SlideSpec, SlideType, SlideTemplate
from .prompt_generator import generate_slide_prompts


def plan_slides(recipe: RecipeData, has_user_image: bool = False) -> list[SlideSpec]:
    """Return exactly 6 SlideSpec objects."""
    prompts = generate_slide_prompts(recipe)  # 4 prompts for slides 1-4

    steps = recipe.steps
    ingredients_text = [f"• {ing}" for ing in recipe.ingredients]
    n = recipe.nutrition

    specs = [
        # Slide 1 — Cover
        SlideSpec(
            index=1,
            slide_type=SlideType.USER_PHOTO if has_user_image else SlideType.AI_GENERATE,
            template=SlideTemplate.COVER,
            prompt=prompts[0] if not has_user_image else None,
            title_text=recipe.title,
            body_lines=[
                f"Prep: {recipe.prep_time_min} min",
                f"Cook: {recipe.cook_time_min} min",
                f"Serves: {recipe.servings}",
            ],
            use_ip_adapter=False,
        ),
        # Slide 2 — Ingredients
        SlideSpec(
            index=2,
            slide_type=SlideType.AI_GENERATE,
            template=SlideTemplate.INGREDIENTS,
            prompt=prompts[1],
            title_text="Ingredients",
            body_lines=ingredients_text,
            use_ip_adapter=True,
        ),
        # Slide 3 — Steps 1 & 2
        SlideSpec(
            index=3,
            slide_type=SlideType.AI_GENERATE,
            template=SlideTemplate.STEPS12,
            prompt=prompts[2],
            title_text="How to Make It",
            body_lines=[
                f"Step 1: {steps[0]}",
                f"Step 2: {steps[1]}",
            ],
            use_ip_adapter=True,
        ),
        # Slide 4 — Steps 3 & 4
        SlideSpec(
            index=4,
            slide_type=SlideType.AI_GENERATE,
            template=SlideTemplate.STEPS34,
            prompt=prompts[3],
            title_text="Almost Done!",
            body_lines=[
                f"Step 3: {steps[2]}",
                f"Step 4: {steps[3]}",
            ],
            use_ip_adapter=True,
        ),
        # Slide 5 — Nutrition (pure Pillow)
        SlideSpec(
            index=5,
            slide_type=SlideType.TEMPLATE_ONLY,
            template=SlideTemplate.NUTRITION,
            title_text="Nutrition per Serving",
            body_lines=[
                f"Calories: {n.calories} kcal",
                f"Protein: {n.protein_g}g",
                f"Carbs: {n.carbs_g}g",
                f"Fat: {n.fat_g}g",
                f"Fiber: {n.fiber_g}g",
            ],
        ),
        # Slide 6 — CTA (pure Pillow)
        SlideSpec(
            index=6,
            slide_type=SlideType.TEMPLATE_ONLY,
            template=SlideTemplate.CTA,
            title_text="Save this recipe!",
            body_lines=[
                "Follow for more healthy recipes",
                "Link in bio for full recipe",
            ],
        ),
    ]

    return specs
