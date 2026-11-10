# RecipeCraft CLI

A beginner-friendly Python command-line recipe scaler and substitution suggestion system.

## Requirements
Python 3.9 or newer. No third-party packages are required.

## Add recipes
Place your existing `.txt` files inside `recipes/`. The filename determines the displayed name. For example, type `Chicken Biryani` to load `Chicken_Biryani.txt`.

Expected file format:

```text
1
Ingredients
200 g, Chicken, Y
100 g, Rice, N
1 tsp, Salt, N
2 tbsp, Yogurt, Y
Recipe
1. Prepare the ingredients.
2. Cook the chicken with the spices.
3. Add rice and cook until ready.
```

Line 1 is original servings (use 1). Ingredient rows contain quantity, ingredient name and Y/N substitute availability. Use the exact headings `Ingredients` and `Recipe`. Avoid commas inside ingredient names because commas separate fields.

## Run
From the project root:

```bash
python main.py
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Quantity scaling
Supported leading quantities: integers (`200 g`), decimals (`1.5 cups`) and fractions (`1/2 tsp`). Units are preserved. Ranges (`1-2 cloves`) and descriptive quantities (`to taste`) are kept unchanged and marked unscaled.

## Modules
- `main.py`: terminal interaction.
- `recipe_loader.py`: discovers and parses recipe files.
- `recipe_scaler.py`: multiplies quantities.
- `dietary_checker.py`: basic keyword screen.
- `substitution_engine.py`: restriction-specific sample alternatives and recursive candidate search with cycle protection.
- `recipe_manager.py`: coordinates the modules and returns one result dictionary.

## Dietary safety
This is an educational prototype, not a medical or allergy-safety checker. Suggestions are examples only. For peanut or gluten allergies, verify the exact product label and cross-contact/manufacturing information. For lactose intolerance, check ingredients and individual tolerance. Never assume a substitute is safe solely because this program suggests it. Certified gluten-free products are important where strict gluten avoidance is required. Peanut allergy users should avoid any candidate ingredient or product unless its safety is confirmed.

## Computational thinking
Lists store ingredients, instructions and restrictions. Dictionaries represent recipes and substitution mappings. Strings are parsed from text files. Nested iteration compares ingredients with restriction keywords. Recursion searches candidate substitutions, while a visited set prevents cycles. Functions are separated into modules.

## Troubleshooting
- No recipes found: add `.txt` files to `recipes/`.
- Recipe not found: enter the filename without `.txt`; spaces and underscores are equivalent.
- Malformed row: each ingredient line must have exactly three comma-separated fields and a Y/N final field.
- Missing headings: use `Ingredients` and `Recipe`.
- Quantity not scaled: unsupported ranges and descriptive quantities are intentionally preserved.
- Import errors: run `python main.py` from the project root.
