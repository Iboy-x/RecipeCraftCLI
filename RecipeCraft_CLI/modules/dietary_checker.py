

KEYWORDS = {
    "lactose intolerance": ["milk", "cream", "butter", "cheese", "yogurt",
                            "yoghurt", "whey", "condensed milk", "milk powder"],
    "peanut allergy": ["peanut", "groundnut"],
    "gluten allergy": ["wheat", "barley", "rye", "flour", "breadcrumbs",
                       "bread", "pasta", "semolina", "couscous", "soy sauce"]
}

def check_dietary_restrictions(ingredients, restrictions):
    conflicts = []
    # Nested iteration: compare every ingredient with each selected restriction keyword.
    for restriction in restrictions:
        for ingredient in ingredients:
            name = ingredient["name"].casefold()
            for keyword in KEYWORDS.get(restriction, []):
                if keyword in name:
                    entry = {"restriction": restriction, "ingredient": ingredient["name"]}
                    if entry not in conflicts:
                        conflicts.append(entry)
    return {
        "status": "BASIC SCREEN ONLY - NOT A SAFETY CERTIFICATION",
        "possible_conflicts": conflicts,
        "is_placeholder": True
    }
