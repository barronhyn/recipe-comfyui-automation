"""Mock LLM: returns hardcoded sample data, no API calls."""
from .models import RecipeData, NutritionInfo, ComparisonData


SAMPLE_RECIPE = RecipeData(
    title="Creamy Garlic Pasta",
    description="A rich and comforting pasta dish with roasted garlic cream sauce.",
    ingredients=[
        "300g spaghetti",
        "6 garlic cloves, minced",
        "200ml heavy cream",
        "50g parmesan, grated",
        "2 tbsp olive oil",
        "Salt & black pepper",
        "Fresh parsley to garnish",
    ],
    steps=[
        "Boil pasta in salted water until al dente. Reserve 1 cup pasta water before draining.",
        "Sauté garlic in olive oil over medium heat for 2 minutes until fragrant and golden.",
        "Pour in cream, simmer 3 minutes. Add parmesan and stir until sauce thickens.",
        "Toss drained pasta in sauce, adding pasta water as needed. Season and serve.",
    ],
    nutrition=NutritionInfo(
        calories=450,
        protein_g=18.0,
        carbs_g=62.0,
        fat_g=16.0,
        fiber_g=3.0,
    ),
    prep_time_min=10,
    cook_time_min=20,
    servings=2,
)


SAMPLE_COMPARISON = ComparisonData(
    product_a_name="Oat Milk",
    product_b_name="Almond Milk",
    calories_a=120,
    calories_b=60,
    price_a=4.99,
    price_b=3.99,
    pros_a=["Higher protein", "Creamy texture", "Good for baristas"],
    cons_a=["More calories", "Contains gluten (some brands)", "Slightly sweet"],
    pros_b=["Low calorie", "Widely available", "Mild flavor"],
    cons_b=["Low protein", "Often contains additives", "Thin consistency"],
    verdict="Oat milk wins for creaminess and nutrition; almond milk wins for calories.",
)


def mock_analyze_food_image(image_bytes: bytes) -> RecipeData:
    return SAMPLE_RECIPE


def mock_generate_recipe_from_text(prompt: str) -> RecipeData:
    recipe = SAMPLE_RECIPE.model_copy()
    if prompt:
        recipe = RecipeData(
            title=prompt.title() if len(prompt) < 40 else "Delicious Recipe",
            description=SAMPLE_RECIPE.description,
            ingredients=SAMPLE_RECIPE.ingredients,
            steps=SAMPLE_RECIPE.steps,
            nutrition=SAMPLE_RECIPE.nutrition,
            prep_time_min=SAMPLE_RECIPE.prep_time_min,
            cook_time_min=SAMPLE_RECIPE.cook_time_min,
            servings=SAMPLE_RECIPE.servings,
        )
    return recipe


def mock_analyze_products(img_a: bytes, img_b: bytes) -> ComparisonData:
    return SAMPLE_COMPARISON
