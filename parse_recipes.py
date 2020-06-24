import re
import io
import json
import sys 
import string

def format_ingredient(raw_string):

# if there is a comma present, split line on “,” and only look at first (zero-ith) substring, else use whole line
# If there is a unit (parentheses are present), just grab the substring before the ( and use the strip method to remove whitespace on the ends (this will allow for situations where the amount is not a number - Ex: Few (drops) hot sauce
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
        ingredientString = " ".join(ingredientSplit)
    else:
        amount = ""
    
    # Checks for parenthesis to find unit type, and removes it from top of the string.
    if ingredientString[0] == "(":
        unit = ingredientString[1:ingredientString.find(")")].strip()
        ingredientSplit = ingredientString.split(")")

         # TODO: Unplural certain unit types when naming them
         
        # There must be a parenthesis at the end of some ingredientString producing errors.  There's definitely a more elegant way to write this block.
        if len(ingredientSplit) > 1:
           ingredientString = ingredientSplit[1].strip()  
        else:
            ingredientString = ingredientSplit[0].strip()
    else:
        unit = ""
        

# Returns remaining ingredientString as "name" value
                                                                                                                                              
    formatted = { 
        "amount": amount,
        "unit": unit,
        "name": ingredientString.strip(),
        "notes": notes,
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
		self.title = string.capwords(recipe_lines[0].strip())
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
				self.ingredients_flat.append({"name": string.capwords(prev_content), "type": "group"})

			# Add ingredient to the list
			if curr_type == "INGREDIENT":
				self.ingredients_flat.append(format_ingredient(curr_content))

			# If there was a subsection header on the steps block, add it to the list
			if prev_type == "TEXT" and curr_type == "STEP":
				self.instructions_flat.append({"name": string.capwords(prev_content), "type": "group"})
			
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

	@staticmethod
	def output_header():
		header_variables = ["title", "json_data", "author", "summary", "ingredients", "instructions"]
		return "\t".join(header_variables)

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
output.write(Recipe.output_header() + "\n")

for r in recipe_list:
	recipe = Recipe(r)
	if recipe is not None: 
		output.write(str(recipe) + "\n")

output.close
input.close
	
