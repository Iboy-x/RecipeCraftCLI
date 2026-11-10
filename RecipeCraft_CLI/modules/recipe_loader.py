from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = ROOT / "recipes"

class RecipeFormatError(ValueError):
    """Raised when a recipe text file has an invalid format."""

def discover_recipes():
    RECIPES_DIR.mkdir(exist_ok=True)
    return sorted(p.name for p in RECIPES_DIR.glob("*.txt") if p.is_file())

def load_recipe(filename):
    # Prevent user input from selecting files outside the recipes directory.
    if Path(filename).name != filename or not filename.lower().endswith(".txt"):
        raise RecipeFormatError("Invalid recipe filename.")
    path = RECIPES_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Recipe '{filename}' was not found.")
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < 4:
        raise RecipeFormatError("Recipe file is too short.")
    try:
        servings = int(lines[0].strip())
    except ValueError:
        raise RecipeFormatError("Line 1 must be the original serving count.")
    if servings < 1:
        raise RecipeFormatError("Original servings must be at least 1.")

    try:
        ingredients_index = next(i for i, line in enumerate(lines)
                                 if line.strip().casefold() == "ingredients")
        recipe_index = next(i for i, line in enumerate(lines)
                            if i > ingredients_index and line.strip().casefold() == "recipe")
    except StopIteration:
        raise RecipeFormatError("File must contain Ingredients and Recipe headings.")

    ingredients = []
    for line_no, line in enumerate(lines[ingredients_index + 1:recipe_index],
                                   start=ingredients_index + 2):
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3 or not parts[0] or not parts[1]:
            raise RecipeFormatError(f"Invalid ingredient row on line {line_no}.")
        if parts[2].upper() not in ("Y", "N"):
            raise RecipeFormatError(f"Line {line_no}: substitute flag must be Y or N.")
        ingredients.append({
            "quantity": parts[0],
            "name": parts[1],
            "substitute_available": parts[2].upper() == "Y"
        })
    if not ingredients:
        raise RecipeFormatError("No ingredients found.")
    instructions = [line.strip() for line in lines[recipe_index + 1:] if line.strip()]
    if not instructions:
        raise RecipeFormatError("No cooking instructions found.")
    return {
        "name": Path(filename).stem.replace("_", " "),
        "filename": filename,
        "original_servings": servings,
        "ingredients": ingredients,
        "instructions": instructions
    }
