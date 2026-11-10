import unittest
from modules.recipe_scaler import scale_quantity
from modules.substitution_engine import find_substitute

class RecipeCraftTests(unittest.TestCase):
    def test_integer_scaling(self):
        self.assertEqual(scale_quantity("200 g", 1, 4), ("800 g", True))

    def test_fraction_scaling(self):
        self.assertEqual(scale_quantity("1/2 tsp", 1, 2), ("1 tsp", True))

    def test_range_is_preserved(self):
        self.assertEqual(scale_quantity("1-2 cloves", 1, 3), ("1-2 cloves", False))

    def test_unavailable_substitute(self):
        self.assertIsNone(find_substitute("milk", ["lactose intolerance"], available=False))

    def test_substitute_suggestion(self):
        self.assertIsNotNone(find_substitute("milk", ["lactose intolerance"]))

if __name__ == "__main__":
    unittest.main()
