import re
import io
import json
import sys 

# TODO: Actually parse the values
# Example final format 
# {
#     "amount": "1",
#     "unit": "cup",
#     "name": "water",
#     "notes": "lukewarm",
#     "type": "ingredient"
# }
def format_ingredient(raw_string):
	formatted = { 
		"amount": "",
		"unit": "",
		"name": raw_string,
		"notes": "",
		"type": "ingredient"
	}
	return formatted

class Recipe:

	def __init__(self, recipe_lines):
		# Print to console if we see this
		if len(recipe_lines) < 2:
			print(recipe_lines)
			return None

		# Parse out the recipe title
		self.title = recipe_lines[0].strip()
		recipe_lines.pop(0)
		
		# Parse out the recipe author if present
		if recipe_lines[0].strip() != "":
			self.author = recipe_lines[0].strip()
			recipe_lines.pop(0)
		else:
			self.author = None
		
		# initialize our content
		self.ingredients_flat = []
		self.instructions_flat = []
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

		for curr_type, curr_content in raw_content:
			# If there was a subsection header on the ingredient block, add it to the list
			if prev_type == "TEXT" and curr_type == "INGREDIENT":
				self.ingredients_flat.append({"name": prev_content, "type": "group"})

			# Add ingredient to the list
			if curr_type == "INGREDIENT":
				self.ingredients_flat.append(format_ingredient(curr_content))

			# If there was a subsection header on the steps block, add it to the list
			if prev_type == "TEXT" and curr_type == "STEP":
				self.instructions_flat.append({"name": prev_content, "type": "group"})
			
			# Add step to the list
			if curr_type == "STEP":
				self.instructions_flat.append({
					"text": "<p>{}<\p>".format(curr_content),
					"type": "instruction",
					"image_url": ""
				})

			# Adding text to the summary
			if prev_type == "TEXT" and (curr_type != "INGREDIENT" and curr_type != "STEP"):
				self.summary = self.summary + "<p>{}<\p>".format(prev_content)

			# Setting the values for the next run through the loop
			prev_type, prev_content = curr_type, curr_content 

		# Save recipe details as JSON
		self.json_format = json.dumps({
			"name": self.title,
			# TODO, add remaining fields
		})

	def __str__(self):
		class_variables = [str(self.title), str(self.json_format), str(self.author), 
						  self.summary, str(self.ingredients_flat), str(self.instructions_flat)]
		return "\t".join(class_variables)


# Start of Code
input_file_name = sys.argv[1] if len(sys.argv) > 1 else "brunkhorst_recipes_formatted.txt"
output_file_name = sys.argv[2] if len(sys.argv) > 2 else "brunkhorst_recipes_formatted.csv"

input = io.open(input_file_name, "r", encoding='utf8')
recipe_list = []
current_recipe = []

# Create recipe_list, a list where each element is a list[String] containing the lines from
# one given recipe
for line in input:
	if "@@@" in line:
		recipe_list.append(current_recipe)
		current_recipe = []
	elif line[0] == "-":
		# Ignore these lines for now, these are typically the recipe section names 
		# Ex: -APPETIZERS AND BEVERAGES-
		continue
	else:
		current_recipe.append(line)

recipe_list.append(current_recipe)

# Parse out details of the recipe and write to output file
output = io.open(output_file_name, "w", encoding='utf8')

for r in recipe_list:
	recipe = Recipe(r)
	if recipe is not None: 
		output.write(str(recipe) + "\n")

output.close
input.close
	
