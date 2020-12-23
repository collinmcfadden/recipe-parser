# recipe-parser
converting the recipe book text to JSON format.


## Running the code
In a Terminal window (Mac) or command prompt (Windows), run the following command

```python parse_recipes.py```

You can specify the input and output filename like so

```python parse_recipes.py fully_formatted_example_recipes.txt fully_formatted_example_recipes.csv```


## Running the unit tests
In a Terminal window (Mac) or command prompt (Windows), run the following command

```python test_parse_recipes.py```



## Style Guide

Style Guide
Using three @ signs to separate each recipe.
@@@
RECIPE TITLE
Authors 


If the ingredients are listed all in one chunk, list them like so (⌘ + Shift + 8)
* Ingredient 1
* Ingredient 2


If the ingredients are in two or more subsections, list them like so (Tab + ⌘ + Shift + 7)
DOUGH
* Ingredient 1
* Ingredient 2


FILLING
* Ingredient 1
* Ingredient 2


The ingredients in the book are listed in two columns. Try to format these so that the ingredients in the first column are listed first and then list the ingredients from the second column.


For the recipe steps, format as a numbered list (⌘ + Shift + 7)
1. In the original cookbook, there weren’t numbers for the steps. Instead, all steps were listed in a single paragraph.
2. Ideally, when you format the recipe, split the sentences out into collections of steps. If nothing else, remove any unnecessary newlines, and have the steps listed all in the number one 


If the Steps are in two or more subsections, list them like so (Tab + ⌘ + Shift + 8)
DOUGH        
1. Step 1
2. Step 2


FILLING        
1. Step 1
2. Step 2


Any chunks of text containing additional recipe details can be left in the same position as they are originally, just try to remove newline characters if you see them.




Phase 2 Style Guide - 
Add a fourth @ before the recipe title when you have applied the formatting
Goals
* Make recipe ingredient values parseable
* Re-read the recipe steps to catch spelling/formatting errors


Making ingredients parsable
Want the ingredients in this format:
* Amount (unit) item name, extra details


Ex. 
* 2 (tbsp) olive oil
* 1 ½ (cups) onion, chopped 
* 1 (tbsp) fresh garlic, minced        
* 3 (6-inch) corn tortillas, cut into 1-inch pieces        
* ½ (cup) heavy cream
* 1 (10 ½ oz can) Ro-Tel tomatoes        
* salt and pepper


Amount
# if there is a comma present, split line on “,” and only look at first (zero-ith) substring, else use whole line
If there is a unit (parentheses are present), just grab the substring before the ( and use the strip method to remove whitespace on the ends (this will allow for situations where the amount is not a number - Ex: Few (drops) hot sauce
Else: use regex to read the the numbers/ unicode fractions at the front of the line
* Regex expression for these fractions https://regexr.com/3p8nd
* Regex search method https://docs.python.org/3/library/re.html#re.search
Empty string if none found


Whole values: 1 (cup)
Compound Fractions: 1 ½ (cups)
Fractions: ½ (cup)
Not present: salt and pepper


Unit 
## NOTE: if comma present in line, split line on “,” and only look at first (zero-ith) substring (because additional recipe details may have parentheses)


Surrounded by parentheses: 1 (cup)


Units that are same whether Amount is <= 1
1 (tsp) vs 2 (tsp)
1 (tbsp) vs 2 (tbsp)
1 (lb) vs 2 (lb)
1 (oz) vs 2 (oz)




Units that are different when Amount is <= 1
½ (cup) vs 1 (cup) vs 1 ½ (cups)
1 (pint) vs 2 (pints)
1 (quart) vs 2 (quarts)
1 can vs 2 cans
(most other units)


Ingredient Name
Ideally listed so that it doesn’t have any commas.  This will not be possible in all cases, such as 
* 1 red, yellow, and green apple, cut into wedges
In this case, the person uploading the recipe will need to manually update the value
Extra Details
Rewrite extra details to be after the ingredient name. Can have additional commas/parentheses, but omit them if they aren’t adding value
Find first comma, if not found, return empty string. else , return second half of line


Common cases:
* 4 (cups) water, boiling         
* 2 (cups) cheese, shredded
* 1 (cup) lemon juice, 4-6 lemons


Original
* 1 (large package).or 3 small packages chicken flavor Rice-a-Roni
* 3 (lb) sweet potatoes (cooked) or 2 (17 oz cans) (drained)
New
* 1 (large package).chicken flavor Rice-a-Roni, or 3 small packages
* 3 (lb) sweet potatoes, cooked or 2 (17 oz cans) drained 


Corner cases to just use your best judgement on
When the recipe has suggests two different ingredients, the second could be recorded as a note or beside the original. The difference in the end is that the note is a lighter gray https://demo.wprecipemaker.com/chic-recipe-template/


I think the first would be more clear than the second
* 1 (stick) butter or oleo, melted        
* 1 (stick) butter, or oleo, melted        


But these cases of alternative ingredients are messy in other recipes, so don’t over think it too much. All in all, we want the info visible clearly on the page, even if it doesn’t properly conform to the variable names that are holding the details. 


* 1 (large bottle/can) pineapple juice, or 1 can concentrate (mixed according to directions)


Way to represent little chef’s notes on the ingredients? E.g:
* 1 (8 oz package) cream cheese (I use ⅓ less fat, don’t use fat free)
* Bacon (I  use the pre-cooked)
Remove parentheses and add a comma between the note and the ingredient:
* 1 (8 oz package) cream cheese, I use ⅓ less fat, don’t use fat free
* Bacon, I use the pre-cooked


