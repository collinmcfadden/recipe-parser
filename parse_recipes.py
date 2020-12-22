import io
import json
import sys 
import string
from recipe import Recipe


# Start of Code
input_file_name = sys.argv[1] if len(sys.argv) > 1 else "brunkhorst_recipes_formatted.txt"
output_file_name = sys.argv[2] if len(sys.argv) > 2 else "brunkhorst_recipes_formatted_dynamo.json"

input = io.open(input_file_name, "r", encoding='utf8')
recipe_list = []
current_recipe = []
current_category = None

# Create recipe_list, a list where each element is a list[String] containing the lines from
# one given recipe
for line in input:
	if "@@@" in line:
		recipe_list.append((current_recipe, current_category))
		current_recipe = []
	elif line[0] == "-":
		# These lines specify the category that the recipe was stored in
		# Ex: -APPETIZERS AND BEVERAGES-
		current_category = string.capwords(line.strip("-").rstrip("-"))
	else:
		current_recipe.append(line.strip())

recipe_list.append((current_recipe, current_category))

# Parse out details of the recipe and write to output file
output = io.open(output_file_name, "w", encoding='utf8')
recipe_dictionary = dict()
recipe_dictionary["Recipe"] = list()
id = 100

for r, category in recipe_list:
	recipe = Recipe(r, f"RECIPE#{id}", category)
	if recipe is not None: 
		recipe_dictionary["Recipe"].append(recipe.dynamo_dictionary())
		id += 1

output.write(json.dumps(recipe_dictionary, indent=4))
output.close
input.close
	
