"""Restriction-aware example substitutions with a recursive search extension point."""

OPTIONS = {
    "milk": {"lactose intolerance": ["lactose-free milk", "unsweetened plant milk"]},
    "cream": {"lactose intolerance": ["lactose-free cream", "unsweetened coconut cream"]},
    "butter": {"lactose intolerance": ["verified dairy-free spread", "olive oil"]},
    "yogurt": {"lactose intolerance": ["lactose-free yogurt", "unsweetened coconut yogurt"]},
    "yoghurt": {"lactose intolerance": ["lactose-free yogurt", "unsweetened coconut yogurt"]},
    "cheese": {"lactose intolerance": ["verified lactose-free cheese", "verified dairy-free cheese"]},
    "peanuts": {"peanut allergy": ["roasted chickpeas", "pumpkin seeds if confirmed safe"]},
    "groundnuts": {"peanut allergy": ["roasted chickpeas", "pumpkin seeds if confirmed safe"]},
    "peanut butter": {"peanut allergy": ["sunflower seed butter if confirmed safe"]},
    "wheat flour": {"gluten allergy": ["certified gluten-free flour blend", "rice flour"]},
    "flour": {"gluten allergy": ["certified gluten-free flour blend", "rice flour"]},
    "breadcrumbs": {"gluten allergy": ["certified gluten-free breadcrumbs"]},
    "bread": {"gluten allergy": ["certified gluten-free bread"]},
    "pasta": {"gluten allergy": ["certified gluten-free pasta"]},
    "soy sauce": {"gluten allergy": ["certified gluten-free tamari"]},
    "barley": {"gluten allergy": ["rice"]},
    "rye": {"gluten allergy": ["certified gluten-free flour blend"]},
    "semolina": {"gluten allergy": ["certified gluten-free flour blend"]},
    "couscous": {"gluten allergy": ["rice or certified gluten-free couscous"]}
}

# Recursive candidate graph; add links here when the substitution database grows.
GRAPH = {
    "milk": ["lactose-free milk", "unsweetened plant milk"],
    "unsweetened plant milk": ["certified gluten-free oat milk"],
    "flour": ["rice flour", "certified gluten-free flour blend"],
    "rice flour": ["certified gluten-free flour blend"]
}

def _recursive_candidate_search(candidates, visited):
    """Recursively inspect candidates. visited prevents cycles."""
    if not candidates:                 # Base case
        return None
    candidate = candidates[0]
    rest = candidates[1:]
    key = candidate.casefold()
    if key in visited:
        return _recursive_candidate_search(rest, visited)
    visited.add(key)
    # Current educational data has no unsafe candidate chains; future rules
    # can recursively inspect GRAPH[key] before accepting a candidate.
    deeper = _recursive_candidate_search(GRAPH.get(key, []), visited)
    if deeper:
        return deeper
    return candidate

def find_substitute(ingredient_name, restrictions=None, visited=None, available=True):
    """Return one suggestion, or None if unavailable/no mapping exists."""
    if not available:
        return None
    restrictions = restrictions or []
    visited = visited if visited is not None else set()
    name = ingredient_name.casefold().strip()
    if name in visited:
        return None
    visited.add(name)
    for restriction in restrictions:
        candidates = OPTIONS.get(name, {}).get(restriction, [])
        if candidates:
            return _recursive_candidate_search(candidates, visited)
    return None
