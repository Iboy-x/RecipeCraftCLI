import re
from fractions import Fraction

NUMBER = re.compile(r"^\s*(\d+\s*/\s*\d+|\d+(?:\.\d+)?)(.*)$")

def scale_quantity(quantity, original_servings, target_servings):
    """Scale leading integer, decimal or fraction; preserve units and unsupported text."""
    if original_servings < 1 or target_servings < 1:
        raise ValueError("Serving counts must be positive.")
    match = NUMBER.match(quantity)
    if not match:
        return quantity, False
    number, unit = match.groups()
    # A hyphen followed by a digit means this is a range (for example 1-2),
    # not a single leading number. Preserve the full text rather than scaling it.
    if re.match(r"^\s*-\s*\d", unit):
        return quantity, False
    try:
        scaled = Fraction(number.replace(" ", "")) * Fraction(target_servings, original_servings)
    except (ValueError, ZeroDivisionError):
        return quantity, False
    if scaled.denominator == 1:
        formatted = str(scaled.numerator)
    else:
        formatted = f"{float(scaled):.3f}".rstrip("0").rstrip(".")
    return formatted + unit, True

def scale_ingredients(ingredients, original_servings, target_servings):
    result = []
    for ingredient in ingredients:
        quantity, scaled = scale_quantity(
            ingredient["quantity"], original_servings, target_servings
        )
        result.append({**ingredient, "scaled_quantity": quantity, "scaled": scaled})
    return result
