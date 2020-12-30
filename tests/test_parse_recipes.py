import unittest
from recipe_parser.ingredients import format_ingredient

class TestIngredient(unittest.TestCase):

    def test_parse_ingredients_no_unit(self):
        line = "1 large onion, sliced"
        formatted = { 
            "amount": "1",
            "unit": "",
            "name": "large onion",
            "notes": "sliced",
            "type": "ingredient"
        }
        self.assertEqual(format_ingredient(line), formatted)

    def test_parse_ingredients_fraction(self):
        line = "⅛ (tsp) pepper"
        formatted = { 
            "amount": "⅛",
            "unit": "tsp",
            "name": "pepper",
            "notes": "",
            "type": "ingredient"
        }
        self.assertEqual(format_ingredient(line), formatted)

    def test_parse_ingredients_compound_fraction(self):
        line = "1 ½ (stalks) celery, sliced or diced"
        formatted = { 
            "amount": "1 ½",
            "unit": "stalks",
            "name": "celery",
            "notes": "sliced or diced",
            "type": "ingredient"
        }
        self.assertEqual(format_ingredient(line), formatted)

    def test_parse_ingredients_range(self):
        line = "4-5 (lb) beef, rump, chuck, or brisket"
        formatted = { 
            "amount": "4-5",
            "unit": "lb",
            "name": "beef",
            "notes": "rump, chuck, or brisket",
            "type": "ingredient"
        }
        self.assertEqual(format_ingredient(line), formatted)

    def test_parse_ingredients_parentheses_after_comma(self):
        line = "6 medium potatoes, peeled, thinly sliced, about 2 (lb)"
        formatted = { 
            "amount": "6",
            "unit": "",
            "name": "medium potatoes",
            "notes": "peeled, thinly sliced, about 2 (lb)",
            "type": "ingredient"
        }
        self.assertEqual(format_ingredient(line), formatted)

    def test_parse_ingredients_numeric_unit(self):
        line = "1 (8 oz package) cream cheese"
        formatted = { 
            "amount": "1",
            "unit": "(8 oz package)",
            "name": "cream cheese",
            "notes": "",
            "type": "ingredient"
        }
        self.assertEqual(format_ingredient(line), formatted)

if __name__ == '__main__':
    unittest.main()