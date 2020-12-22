from abc import ABC, abstractmethod


class IngredientBase(ABC):

	@abstractmethod
	def add_ingredient(self, ingredient_dict):
		pass

	@abstractmethod
	def get_json(self):
		pass


class Ingredients(IngredientBase):

	def __init__(self):
		self.type = "ingredients"
		self.ingredients = []

	def add_ingredient(self, ingredient_dict):
		self.ingredients.append(ingredient_dict)

	def get_json(self):
		return {
			"type": self.type,
			"items": self.ingredients
		}


class SplitIngredients(IngredientBase):

	def __init__(self): 
		self.type = "split_ingredients"
		self.split_ingredients = []
		self.current_section = None

	def set_section_title(self, title): 
		if self.current_section is not None:
			self.split_ingredients.append(self.current_section)

		self.current_section = {
			"title": {"S": title},
			"items": []
		}

	def add_ingredient(self, ingredient_dict):
		self.current_section["items"].append(ingredient_dict)

	def get_json(self):
		if self.current_section is not None:
			self.split_ingredients.append(self.current_section)
			self.current_section = None

		return {
			"type": {"S": self.type},
			"split_ingredients": self.split_ingredients
		}


def format_ingredient(raw_string):

# if there is a comma present, split line on “,” and only look at first (zero-ith) substring, else use whole line
# If there is a unit (parentheses are present), just grab the substring before the ( and use the strip method to remove whitespace on the ends (this will allow for situations where the amount is not a number - Ex: Few (drops) hot sauce
	
	#init values
	ingredientString = ""
	notes = ""
	
# Checks for a comma and makes notes if needed    
	if "," in raw_string:
		ingredientNotesSplit = raw_string.split(",")
		notes = ",".join(ingredientNotesSplit[1:]).strip()
		ingredientString = ingredientNotesSplit[0]
	else:
		ingredientString = raw_string
		notes = ""
   
	# Checks for number or fraction at top of string, records the amount, and removes the number/fraction
	if ingredientString[0].isnumeric():
		ingredientSplit = ingredientString.split(" ")
		amount = ingredientSplit.pop(0)

		# In the case of compound fractions, adds the fraction to the amount
		if ingredientSplit[0].isnumeric():
			amount = "{} {}".format(amount, ingredientSplit[0])
			ingredientSplit.pop(0)

		ingredientString = " ".join(ingredientSplit).strip()
	else:
		amount = ""
	
	# Checks for parenthesis to find unit type, and removes it from top of the string.
	if ingredientString[0] == "(":
		endParenthesisIndex = ingredientString.find(")")
		unit = ingredientString[1:endParenthesisIndex].strip()
		ingredientString = ingredientString[endParenthesisIndex+1:]

		# If unit starts with a number, surrond unit with parentheses. 
		# Ex: 8 oz package -> (8 oz package) so that the line can read: 1 (8 oz package) cream cheese
		if len(unit) > 0 and unit[0].isnumeric():
			unit = "({})".format(unit)

		 # TODO: Unplural certain unit types when naming them

	else:
		unit = ""

# Returns remaining ingredientString as "name" value                                                                                                                         
	return { 
		"amount": {"S": amount},
		"unit": {"S": unit},
		"name": {"S": ingredientString.strip()},
		"notes": {"S": notes},
		"full_string": {"S": format_full_string(amount, unit, ingredientString, notes)}
	}

def format_full_string(amount, unit, ingredient_string, notes):
	formatted = f"{amount} {unit} {ingredient_string.strip()}".strip()
	if notes is not "":
		formatted = formatted + f" - {notes}"

	while "  " in formatted: 
		formatted = formatted.replace("  ", " ")
	return formatted