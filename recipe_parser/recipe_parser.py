import io
import json
import sys 
import string
from recipe import Recipe
from collection import Collection

import random
random.seed(0)

input_file_name = sys.argv[1] if len(sys.argv) > 1 else "./input/brunkhorst_recipes_formatted.txt"
output_file_name = sys.argv[2] if len(sys.argv) > 2 else "./output/brunkhorst_recipes_formatted_dynamo.json"

input_file = io.open(input_file_name, "r", encoding='utf8')

# List of tuples. The first element in each tuple is a list of all the raw lines in the recipe. 
# Second element is the Category object associated with the recipe
raw_recipe_list = []
# List of raw lines of the recipe
current_recipe_raw_lines = []

current_collection = None
collection_id = 100
collection_list = []

# Create the list of raw recipe details
for line in input_file:
	if "@@@" in line:
		# @@@ is the delimiter between recipes. When this is encountered, append the current list of lines
		# to recipe_list and create a new list of lines for the next recipe
		raw_recipe_list.append((current_recipe_raw_lines, current_collection))
		current_recipe_raw_lines = []
	elif line[0] == "-":
		# These lines specify the collection that the recipe was stored in
		# Ex: -APPETIZERS AND BEVERAGES
		collection_str = string.capwords(line.strip("-"))
		current_collection = Collection(collection_id, collection_str)
		collection_list.append(current_collection)
		collection_id += 1
	else: 
		# Append all other lines
		current_recipe_raw_lines.append(line.strip())


recipe_id = 100
recipe_class_list = list()

# Create a list of the recipe rows in the dynamo table and the 
for raw_recipe_list, collection in raw_recipe_list:
	recipe = Recipe(raw_recipe_list, recipe_id, collection)
	if recipe is not None and hasattr(recipe, "title"):
		recipe_class_list.append(recipe)
		recipe_id += 1

# Now that the recipes have been parsed and added to Collections, cycle through each collection
# If a collection has less than 10 members, prompt user input to ask what other collections of 
# recipes should be suggested by its recipes
# Ex. "Main Dish - Turkey" collection has only one member, so "Main Dish - Chicken" recipes should be used as additional recipe suggestions
print(", ".join([f"{index}: {collection.name}" for index, collection in enumerate(collection_list)]))

for collection in collection_list:
	num_recipes = len(collection.recipe_list)

	# We want 10 suggestions per recipe, so need to ensure there are 11 available in the collections (because a recipe can't recommend itself - that would be narcissistic)
	while num_recipes < 11:
		additional_collection_index = input((f"Need {11 - num_recipes} more recipes to suggest to {collection.name}. "
											 f"Enter the index of the collection that should be used for additional recommendations."))
		# Ensure user input data quality
		if additional_collection_index.isdigit() and not 0 <= int(additional_collection_index) < len(collection_list):
			print(f"Input of {additional_collection_index} is invalid. Must be integer from 0-{len(collection_list) - 1}.")
		else:
			backup_collection = collection_list[int(additional_collection_index)]
			collection.backup_collections.append(backup_collection)
			num_recipes += len(backup_collection.recipe_list)

# Add the Dynamo JSON details to our running list of dynamo records to upload
dynamo_records = list()

# For each collection, add the records to the dynamo list
for collection in collection_list:
	dynamo_records.append(collection.get_dynamo_dictionary())

# For each recipe, randomly generate recipe suggestion from recipes in its category/backup categories
for recipe in recipe_class_list:
	print(recipe.title)
	dynamo_records.extend(recipe.get_dynamo_dictionaries())
	dynamo_records.extend(recipe.collection.get_recipe_suggestions(recipe))

# Write lines to output file
output_file = io.open(output_file_name, "w", encoding='utf8')
recipe_dictionary = {"Recipe": dynamo_records}

output_file.write(json.dumps(recipe_dictionary, indent=4))
output_file.close
input_file.close
	
