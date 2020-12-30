import re
import json
import string
from instructions import Steps, SplitSteps
from ingredients import Ingredients, SplitIngredients, format_ingredient
from util import slug
from collection import Collection


class Recipe:

	def __init__(self, recipe_lines, id, collection):
		# Print to console if we see this
		if len(recipe_lines) < 2:
			print(recipe_lines)
			return None

		# Parse out the recipe title
		self.title = string.capwords(recipe_lines[0].strip())
		self.slug = slug(self.title)
		self.id = id
		self.recipe_id = f"RECIPE#{id}"
		recipe_lines.pop(0)
		
		self.collection = collection
		if self.collection is not None:
			self.collection_to_recipe_mapping, self.recipe_to_collection_mapping = collection.add_recipe(self)
		else:
			print(f"recipe {self.title} has no collection")

		# Parse out the recipe author if present
		if recipe_lines[0].strip() != "":
			self.author = recipe_lines[0].strip()
			recipe_lines.pop(0)
		else:
			self.author = None
		
		# initialize our content
		self.ingredients_class = None
		self.instructions_class = None
		self.summary = ""

		# Label lines based on the content they contain
		raw_content = []
		for line in recipe_lines:
			line = line.strip()
						
			if line == "":
				raw_content.append(("BLANK", line))
			elif re.search("^[*]", line):
				raw_content.append(("INGREDIENT", line.lstrip("*").strip()))
			elif re.search("^\d", line):
				raw_content.append(("STEP", line.lstrip("0123456789.").strip()))
			else:
				raw_content.append(("TEXT", line))
		
		# Add extra value to array so that we capture all elements of the list and at least have one element
		raw_content.insert(0, ("BLANK", ""))
		raw_content.append(("BLANK", ""))
		
		# Save the contents of each line to the proper variable
		prev_type, prev_content = None, None

		try:
			for curr_type, curr_content in raw_content:
				# If there was a subsection header on the ingredient block, add it to the list
				if prev_type == "TEXT" and curr_type == "INGREDIENT":
					if self.ingredients_class is None: 
						self.ingredients_class = SplitIngredients()
					self.ingredients_class.set_section_title(string.capwords(prev_content).strip(":"))

				# Add ingredient to the list
				if curr_type == "INGREDIENT":
					if self.ingredients_class is None:
						self.ingredients_class = Ingredients()
					self.ingredients_class.add_ingredient(format_ingredient(curr_content))

				# If there was a subsection header on the steps block, add it to the list
				if prev_type == "TEXT" and curr_type == "STEP":
					if self.instructions_class is None: 
						self.instructions_class = SplitSteps()
					self.instructions_class.set_section_title(string.capwords(prev_content).strip(":"))
				
				# Add step to the list
				if curr_type == "STEP":
					if self.instructions_class is None:
						self.instructions_class = Steps()
					self.instructions_class.add_instruction(curr_content)

				# Adding text to the summary
				if prev_type == "TEXT" and (curr_type != "INGREDIENT" and curr_type != "STEP"):
					self.summary = self.summary + prev_content

				# Setting the values for the next run through the loop
				prev_type, prev_content = curr_type, curr_content 
		except AttributeError as err:
			print(f"Error parsing recipe: {err}")
			print(recipe_lines)
			raise

		self.dynamo_dict = {
			"PutRequest": {
				"Item": {
					"PK": {"S": self.recipe_id},
					"SK": {"S": self.recipe_id},
					"id": {"N": self.id},
					"name": {"S": self.title},
					"slug": {"S": self.slug},
					"author": {"M": {
						"name" : { "S" : self.author}
					}},
					"description": {"S": self.summary},
					"ingredients": self.ingredients_class.get_json() if self.ingredients_class is not None else None,
					"instructions": self.instructions_class.get_json() if self.instructions_class is not None else None
				}
			}
		}

	def get_dynamo_dictionaries(self):
		return [
			self.dynamo_dict,
			self.collection_to_recipe_mapping,
			self.recipe_to_collection_mapping
		]


