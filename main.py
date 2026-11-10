from pathlib import Path
import re
from fractions import Fraction

# SECTION 1: RECIPE LOADER

ROOT_FOLDER = Path(__file__).resolve().parent
RECIPES_FOLDER = ROOT_FOLDER / "recipes"
DEMO_MODE = True


class RecipeFormatError(ValueError):
    """Raised when a recipe text file does not follow the required format."""


def discover_recipes():
    """Find all .txt recipe files in the recipes folder."""
    RECIPES_FOLDER.mkdir(exist_ok=True)
    return sorted(
        file.name for file in RECIPES_FOLDER.glob("*.txt") if file.is_file()
    )


def load_recipe(filename):
    """Read a recipe file and convert its contents into Python dictionaries."""
    # Prevent a filename from being used to access files outside the recipes folder.
    if Path(filename).name != filename or not filename.lower().endswith(".txt"):
        raise RecipeFormatError("Invalid recipe filename.")

    file_path = RECIPES_FOLDER / filename
    if not file_path.is_file():
        raise FileNotFoundError(f"Recipe '{filename}' was not found.")

    lines = file_path.read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < 4:
        raise RecipeFormatError("Recipe file is too short.")

    try:
        original_servings = int(lines[0].strip())
    except ValueError:
        raise RecipeFormatError("Line 1 must contain the original serving count.")

    if original_servings < 1:
        raise RecipeFormatError("Original servings must be at least 1.")

    try:
        ingredients_index = next(
            i for i, line in enumerate(lines)
            if line.strip().casefold() == "ingredients"
        )
        recipe_index = next(
            i for i, line in enumerate(lines)
            if i > ingredients_index and line.strip().casefold() == "recipe"
        )
    except StopIteration:
        raise RecipeFormatError("The file must contain Ingredients and Recipe headings.")

    ingredients = []

    # Iteration: read each ingredient row and turn it into a dictionary.
    for line_number, line in enumerate(
        lines[ingredients_index + 1:recipe_index],
        start=ingredients_index + 2
    ):
        if not line.strip():
            continue

        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3 or not parts[0] or not parts[1]:
            raise RecipeFormatError(f"Invalid ingredient row on line {line_number}.")

        if parts[2].upper() not in ("Y", "N"):
            raise RecipeFormatError(
                f"Line {line_number}: substitute flag must be Y or N."
            )

        ingredients.append({
            "quantity": parts[0],
            "name": parts[1],
            "substitute_available": parts[2].upper() == "Y"
        })

    if not ingredients:
        raise RecipeFormatError("No ingredients were found.")

    instructions = [
        line.strip() for line in lines[recipe_index + 1:] if line.strip()
    ]
    if not instructions:
        raise RecipeFormatError("No cooking instructions were found.")

    return {
        "name": Path(filename).stem.replace("_", " "),
        "filename": filename,
        "original_servings": original_servings,
        "ingredients": ingredients,
        "instructions": instructions
    }


# SECTION 2: RECIPE SCALER

# Recognises quantities such as 2, 1.5, and 3/4 at the beginning of a string.
NUMBER_PATTERN = re.compile(r"^\s*(\d+\s*/\s*\d+|\d+(?:\.\d+)?)(.*)$")


def scale_quantity(quantity, original_servings, target_servings):
    """Scale a number at the start of a quantity while preserving its unit."""
    if original_servings < 1 or target_servings < 1:
        raise ValueError("Serving counts must be positive.")

    match = NUMBER_PATTERN.match(quantity)
    if not match:
        return quantity, False

    number, unit = match.groups()

    # Do not accidentally scale ranges such as '1-2 cloves'.
    if re.match(r"^\s*-\s*\d", unit):
        return quantity, False

    try:
        amount = Fraction(number.replace(" ", ""))
        scaled_amount = amount * Fraction(target_servings, original_servings)
    except (ValueError, ZeroDivisionError):
        return quantity, False

    if scaled_amount.denominator == 1:
        formatted_amount = str(scaled_amount.numerator)
    else:
        formatted_amount = f"{float(scaled_amount):.3f}".rstrip("0").rstrip(".")

    return formatted_amount + unit, True


def scale_ingredients(ingredients, original_servings, target_servings):
    """Return a new list containing scaled ingredient dictionaries."""
    scaled_list = []

    for ingredient in ingredients:
        new_quantity, was_scaled = scale_quantity(
            ingredient["quantity"], original_servings, target_servings
        )
        scaled_item = {
            **ingredient,
            "scaled_quantity": new_quantity,
            "scaled": was_scaled
        }
        scaled_list.append(scaled_item)

    return scaled_list


# ============================================================
# SECTION 3: DIETARY RESTRICTION CHECKER
# ============================================================

DIETARY_KEYWORDS = {
    "lactose intolerance": [
        "milk", "cream", "butter", "cheese", "yogurt", "yoghurt",
        "whey", "condensed milk", "milk powder"
    ],
    "peanut allergy": ["peanut", "groundnut"],
    "gluten allergy": [
        "wheat", "barley", "rye", "flour", "breadcrumbs", "bread",
        "pasta", "semolina", "couscous", "soy sauce"
    ]
}


def check_dietary_restrictions(ingredients, restrictions):
    """Find possible ingredient conflicts using a basic keyword screen."""
    possible_conflicts = []

    # Nested iteration: compare every ingredient with every selected restriction.
    for restriction in restrictions:
        for ingredient in ingredients:
            ingredient_name = ingredient["name"].casefold()

            for keyword in DIETARY_KEYWORDS.get(restriction, []):
                if keyword in ingredient_name:
                    conflict = {
                        "restriction": restriction,
                        "ingredient": ingredient["name"]
                    }
                    if conflict not in possible_conflicts:
                        possible_conflicts.append(conflict)

    return {
        "status": "BASIC SCREEN ONLY - NOT A SAFETY CERTIFICATION",
        "possible_conflicts": possible_conflicts
    }


# ============================================================
# SECTION 4: SUBSTITUTION ENGINE (DICTIONARIES + RECURSION)
# ============================================================

SUBSTITUTION_OPTIONS = {
    "milk": {
        "lactose intolerance": ["lactose-free milk", "unsweetened plant milk"]
    },
    "cream": {
        "lactose intolerance": ["lactose-free cream", "unsweetened coconut cream"]
    },
    "butter": {
        "lactose intolerance": ["verified dairy-free spread", "olive oil"]
    },
    "yogurt": {
        "lactose intolerance": ["lactose-free yogurt", "unsweetened coconut yogurt"]
    },
    "yoghurt": {
        "lactose intolerance": ["lactose-free yogurt", "unsweetened coconut yogurt"]
    },
    "cheese": {
        "lactose intolerance": [
            "verified lactose-free cheese", "verified dairy-free cheese"
        ]
    },
    "peanuts": {
        "peanut allergy": ["roasted chickpeas", "pumpkin seeds if confirmed safe"]
    },
    "groundnuts": {
        "peanut allergy": ["roasted chickpeas", "pumpkin seeds if confirmed safe"]
    },
    "peanut butter": {
        "peanut allergy": ["sunflower seed butter if confirmed safe"]
    },
    "wheat flour": {
        "gluten allergy": ["certified gluten-free flour blend", "rice flour"]
    },
    "flour": {
        "gluten allergy": ["certified gluten-free flour blend", "rice flour"]
    },
    "breadcrumbs": {
        "gluten allergy": ["certified gluten-free breadcrumbs"]
    },
    "bread": {
        "gluten allergy": ["certified gluten-free bread"]
    },
    "pasta": {
        "gluten allergy": ["certified gluten-free pasta"]
    },
    "soy sauce": {
        "gluten allergy": ["certified gluten-free tamari"]
    },
    "barley": {"gluten allergy": ["rice"]},
    "rye": {
        "gluten allergy": ["certified gluten-free flour blend"]
    },
    "semolina": {
        "gluten allergy": ["certified gluten-free flour blend"]
    },
    "couscous": {
        "gluten allergy": ["rice or certified gluten-free couscous"]
    }
}

# A small recursive candidate graph. It can be expanded with more options.
SUBSTITUTION_GRAPH = {
    "milk": ["lactose-free milk", "unsweetened plant milk"],
    "unsweetened plant milk": ["certified gluten-free oat milk"],
    "flour": ["rice flour", "certified gluten-free flour blend"],
    "rice flour": ["certified gluten-free flour blend"]
}


def recursive_candidate_search(candidates, visited):
    """Recursively search candidates; visited prevents repeated/cyclic searches."""
    # Base case: there are no candidates left.
    if not candidates:
        return None

    candidate = candidates[0]
    remaining_candidates = candidates[1:]
    candidate_key = candidate.casefold()

    if candidate_key in visited:
        return recursive_candidate_search(remaining_candidates, visited)

    visited.add(candidate_key)

    # Recursion: search any alternatives connected to this candidate.
    deeper_option = recursive_candidate_search(
        SUBSTITUTION_GRAPH.get(candidate_key, []), visited
    )
    if deeper_option:
        return deeper_option

    return candidate


def find_substitute(ingredient_name, restrictions=None, visited=None, available=True):
    """Find one substitution for an ingredient and selected restriction(s)."""
    if not available:
        return None

    restrictions = restrictions or []
    if visited is None:
        visited = set()

    ingredient_key = ingredient_name.casefold().strip()
    if ingredient_key in visited:
        return None
    visited.add(ingredient_key)

    for restriction in restrictions:
        candidates = SUBSTITUTION_OPTIONS.get(ingredient_key, {}).get(restriction, [])
        if candidates:
            return recursive_candidate_search(candidates, visited)

    return None


# ============================================================
# SECTION 5: RECIPE MANAGER
# ============================================================

def prepare_recipe(filename, target_servings, restrictions=None):
    """Coordinate loading, scaling, dietary screening, and substitutions."""
    if target_servings < 1:
        raise ValueError("Serving count must be at least 1.")

    restrictions = restrictions or []
    recipe = load_recipe(filename)

    adjusted_ingredients = scale_ingredients(
        recipe["ingredients"], recipe["original_servings"], target_servings
    )
    dietary_result = check_dietary_restrictions(
        recipe["ingredients"], restrictions
    )

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
        "ingredients": adjusted_ingredients,
        "dietary_check": dietary_result,
        "substitutions": substitutions
    }


# ============================================================
# SECTION 6: USER INTERFACE / MAIN PROGRAM
# ============================================================

def choose_recipe(recipe_files):
    """Ask the user to choose one of the available recipe files."""
    print("\nAvailable recipes:")
    for filename in recipe_files:
        print(" -", filename[:-4].replace("_", " "))

    while True:
        chosen_name = input("\nWhat would you like to cook? ").strip()
        chosen_name = chosen_name.casefold().replace(" ", "_")

        matching_files = [
            filename for filename in recipe_files
            if filename[:-4].casefold() == chosen_name
        ]

        if matching_files:
            return matching_files[0]

        print("Recipe not found. Please try again.")


def ask_servings():
    """Get a valid positive whole-number serving count from the user."""
    while True:
        try:
            servings = int(input("How many people are you cooking for? "))
            if servings >= 1:
                return servings
        except ValueError:
            pass

        print("Please enter a whole number of at least 1.")


def ask_restrictions():
    """Let the user select one or more dietary restrictions."""
    options = {
        "1": "lactose intolerance",
        "2": "peanut allergy",
        "3": "gluten allergy"
    }

    print("\nDietary restrictions:")
    print("1 = Lactose intolerance")
    print("2 = Peanut allergy")
    print("3 = Gluten allergy")
    print("Enter numbers separated by commas, or 0 for none.")

    while True:
        answer = input("Your choice: ").strip()

        if answer in ("", "0"):
            return []

        choices = [choice.strip() for choice in answer.split(",")]
        if all(choice in options for choice in choices):
            # dict.fromkeys removes duplicate choices while preserving order.
            return list(dict.fromkeys(options[choice] for choice in choices))

        print("Invalid choice. Example: 1,3")


def display_result(result):
    """Display the basic prepared-recipe workflow for the checkpoint demo."""
    recipe = result["recipe"]

    print("\n" + "=" * 58)
    if DEMO_MODE:
        print("CHECKPOINT DEMO - BASIC FUNCTIONALITY")
    print(recipe["name"].upper(), "| Servings:", result["target_servings"])
    print("Multiplier:", result["multiplier"], "x")

    print("\nINGREDIENTS")
    for ingredient in result["ingredients"]:
        flag = "Y" if ingredient["substitute_available"] else "N"
        note = "" if ingredient["scaled"] else " [quantity not scaled]"
        print(
            f"- {ingredient['scaled_quantity']} {ingredient['name']} "
            f"[Substitute available: {flag}]{note}"
        )

    print("\nSUBSTITUTION SUGGESTIONS")
    if result["substitutions"]:
        for substitution in result["substitutions"]:
            print(
                f"- {substitution['ingredient']} -> "
                f"{substitution['alternative']}"
            )
            print("  Check product labels and cross-contact information.")
    else:
        print("- No matching available substitutions found.")

    print("\nINSTRUCTIONS")
    for step in recipe["instructions"]:
        print(step)

    print("=" * 58)


def display_error(error):
    """Show a useful next step without exposing internal implementation details."""
    if isinstance(error, FileNotFoundError):
        print("Sorry, that recipe is not available right now.")
    elif isinstance(error, (ValueError, RecipeFormatError)):
        print("Sorry, this recipe could not be prepared with those details.")
    else:
        print("Sorry, something went wrong while preparing the recipe.")
    print("Please check your choices and try again.")


def main():
    """Run the RecipeCraft command-line application."""
    print("\nRECIPECRAFT - Recipe Scaling & Substitution")
    if DEMO_MODE:
        print("Checkpoint demo: showing the basic recipe workflow.")
    recipe_files = discover_recipes()

    if not recipe_files:
        print("No recipe files found.")
        print("Create a 'recipes' folder beside main.py and add .txt recipe files.")
        return

    while True:
        filename = choose_recipe(recipe_files)
        servings = ask_servings()
        restrictions = ask_restrictions()

        try:
            result = prepare_recipe(filename, servings, restrictions)
            display_result(result)
        except (ValueError, FileNotFoundError) as error:
            display_error(error)

        another = input("\nPrepare another recipe? (y/n): ").strip().casefold()
        if another != "y":
            print("Thanks for using RecipeCraft!")
            break


# This condition starts the program only when this file is run directly.
if __name__ == "__main__":
    main()
