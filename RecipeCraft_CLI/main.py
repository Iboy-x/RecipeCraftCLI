from modules.recipe_loader import discover_recipes
from modules.recipe_manager import prepare_recipe

def choose_recipe(files):
    print("\nAvailable recipes:")
    for filename in files:
        print(" -", filename[:-4].replace("_", " "))
    while True:
        name = input("\nWhat would you like to cook? ").strip().casefold().replace(" ", "_")
        matches = [f for f in files if f[:-4].casefold() == name]
        if matches:
            return matches[0]
        print("Recipe not found. Try again.")

def ask_servings():
    while True:
        try:
            value = int(input("How many people are you cooking for? "))
            if value >= 1:
                return value
        except ValueError:
            pass
        print("Enter a whole number of at least 1.")

def ask_restrictions():
    options = {"1": "lactose intolerance", "2": "peanut allergy", "3": "gluten allergy"}
    print("\nRestrictions: 1=Lactose intolerance, 2=Peanut allergy, 3=Gluten allergy")
    print("Enter numbers separated by commas, or 0 for none.")
    while True:
        answer = input("Your choice: ").strip()
        if answer in ("", "0"):
            return []
        choices = [x.strip() for x in answer.split(",")]
        if all(x in options for x in choices):
            return list(dict.fromkeys(options[x] for x in choices))
        print("Invalid choice. Example: 1,3")

def display_result(result):
    recipe = result["recipe"]
    print("\n" + "=" * 54)
    print(recipe["name"].upper(), "| Servings:", result["target_servings"])
    print("Multiplier:", result["multiplier"], "x")
    print("\nINGREDIENTS")
    for item in result["ingredients"]:
        flag = "Y" if item["substitute_available"] else "N"
        note = "" if item["scaled"] else " [not scaled: unsupported format]"
        print(f"- {item['scaled_quantity']} {item['name']} [Substitute: {flag}]{note}")

    print("\nDIETARY SCREEN:", result["dietary_check"]["status"])
    if result["dietary_check"]["possible_conflicts"]:
        for conflict in result["dietary_check"]["possible_conflicts"]:
            print(f"- Possible {conflict['restriction']} conflict: {conflict['ingredient']}")
    else:
        print("- No obvious keyword matches found.")
    print("This basic keyword screen is NOT an allergy-safety guarantee.")

    print("\nSUBSTITUTION SUGGESTIONS")
    if result["substitutions"]:
        for item in result["substitutions"]:
            print(f"- {item['ingredient']} -> {item['alternative']}")
            print("  Verify product labels and cross-contact information.")
    else:
        print("- No matching available substitutions found.")

    print("\nINSTRUCTIONS")
    for step in recipe["instructions"]:
        print(step)
    print("=" * 54)

def main():
    print("\nRECIPECRAFT - Smart Recipe Scaling & Substitution")
    files = discover_recipes()
    if not files:
        print("No .txt recipes found. Add your files to the recipes folder.")
        return
    while True:
        filename = choose_recipe(files)
        servings = ask_servings()
        restrictions = ask_restrictions()
        try:
            display_result(prepare_recipe(filename, servings, restrictions))
        except (ValueError, FileNotFoundError) as error:
            print("Could not prepare recipe:", error)
        if input("\nPrepare another recipe? (y/n): ").strip().casefold() != "y":
            print("Thanks for using RecipeCraft!")
            break

if __name__ == "__main__":
    main()
