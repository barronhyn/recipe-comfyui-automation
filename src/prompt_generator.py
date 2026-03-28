"""Generate ComfyUI image prompts from RecipeData."""
from .models import RecipeData

_QUALITY_SUFFIX = (
    "4k, professional photography, food magazine quality, sharp focus, beautiful lighting"
)


def _ingredient_list(recipe: RecipeData, max_items: int = 5) -> str:
    items = recipe.ingredients[:max_items]
    return ", ".join(items)


def generate_slide_prompts(recipe: RecipeData) -> list[str]:
    """Return 4 prompts for slides 1-4. Slides 5-6 use Pillow only."""
    title = recipe.title

    cover = (
        f"professional food photography of {title}, "
        f"top-down view, studio lighting, clean white plate, "
        f"{_QUALITY_SUFFIX}"
    )

    ingredients = (
        f"flat lay of {_ingredient_list(recipe)} on white marble countertop, "
        f"top-down, soft natural light, food styling, "
        f"clean composition with negative space for text overlay, "
        f"{_QUALITY_SUFFIX}"
    )

    step1 = recipe.steps[0][:60]
    steps12 = (
        f"close-up cooking scene: {step1}, kitchen, "
        f"warm ambient light, process photography, steam, "
        f"{_QUALITY_SUFFIX}"
    )

    step3 = recipe.steps[2][:60]
    steps34 = (
        f"cooking close-up: {step3}, rustic kitchen background, "
        f"warm golden hour lighting, food content creator style, "
        f"{_QUALITY_SUFFIX}"
    )

    return [cover, ingredients, steps12, steps34]
