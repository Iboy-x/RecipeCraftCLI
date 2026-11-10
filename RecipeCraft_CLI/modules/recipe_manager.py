from modules.recipe_loader import load_recipe
from modules.recipe_scaler import scale_ingredients
from modules.dietary_checker import check_dietary_restrictions
from modules.substitution_engine import find_substitute

def prepare_recipe(filename, target_servings, restrictions=None):
    """Load, scale, screen and prepare substitutions for one recipe."""
    if target_servings < 1:
        raise ValueError("Serving count must be at least 1.")
    restrictions = restrictions or []
    recipe = load_recipe(filename)
    adjusted = scale_ingredients(
        recipe["ingredients"], recipe["original_servings"], target_servings
    )
    dietary = check_dietary_restrictions(recipe["ingredients"], restrictions)
    substitutions = []
    for ingredient in recipe["ingredients"]:
        if ingredient["substitute_available"]:
            alternative = find_substitute(
                ingredient["name"], restrictions, available=True
            )
            if alternative:
                substitutions.append({
                    "ingredient": ingredient["name"],
                    "alternative": alternative
                })
    return {
        "recipe": recipe,
        "target_servings": target_servings,
        "multiplier": target_servings / recipe["original_servings"],
        "restrictions": restrictions,
        "ingredients": adjusted,
        "dietary_check": dietary,
        "substitutions": substitutions
    }
