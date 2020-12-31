from util import slug
from copy import deepcopy
import random

random.seed(0)

class Collection():

	def __init__(self, id, name):
		self.collection_id = f"COLLECTION#{id}"
		self.id = id
		self.name = name
		self.recipe_list = []
		self.slug = slug(self.name)

		# When creating initial 10 recipe suggestions based on a given recipe, we will source those from 
		# the other recipes in their collection. If a collection has less than 10 total recipes, we will source from 
		# this list of backup collections to supply the additional recipe suggestions
		self.backup_collections = []

	def get_dynamo_dictionary(self):
		return {
			"PutRequest": {
				"Item": {
					"PK": {"S": self.collection_id},
					"SK": {"S": self.collection_id},
					"id": {"N": self.id},
					"name": {"S": self.name},
					"slug": {"S": self.slug},
					"description": {"S": "This is a default description of what the collection contains!"},
				}
			}
		}

	def add_recipe(self, recipe):
		"""
		In the DynamoDB table, we are mapping a many-to-many relationship within a single table.
		The two keys on the table are:
			Partition Key: PK
			Sort Key: SK

		To map the relationship between collections and their recipes. 

		PK				SK
		RECIPE#1		RECIPE#1			- Provides the full details of the recipe
		COLLECTION#1	COLLECTION#1 		- Provides the full details of the collection

		# collection_to_recipe_mapping
		COLLECTION#1	RECIPE#1			- Provides only subset of recipe details needed to preview
		COLLECTION#1	RECIPE#2			- One Collection can have many recipes with one dynamo record per relationship

		# recipe_to_collection_mapping
		RECIPE#1		COLLECTION#1		- Provides only a subset of the collection details needed to preview
		RECIPE#1		COLLECTION#2		- One Recipe can have many collections with one dynamo record per relationship

		We require mapping in both directions even if we don't have a usecase for the recipe to collection mapping
		at the moment, because if a recipe is deleted, we can use this record to know to delete the recipe from 
		its categories

		More details on this style of DynamoDB relationship here 
		https://medium.com/@kaushikthedeveloper/many-to-many-relation-in-dynamodb-8e948ed38d8d
		"""
		self.recipe_list.append(recipe)
		collection_to_recipe_mapping = {
			"PutRequest": {
				"Item": {
					"PK": {"S": self.collection_id},
					"SK": {"S": recipe.recipe_id},
					"id": {"N": recipe.id},
					"name": {"S": recipe.title},
					"slug": {"S": recipe.slug},
				}
			}
		}

		recipe_to_collection_mapping = {
			"PutRequest": {
				"Item": {
					"PK": {"S": recipe.recipe_id},
					"SK": {"S": self.collection_id},
					"id": {"N": self.id},
					"name": {"S": self.name},
					"slug": {"S": self.slug},
				}
			}
		}
		return collection_to_recipe_mapping, recipe_to_collection_mapping

	def get_recipe_suggestions(self, recipe):
		"""
		Based on the other recipes in the category/backup categories, provide recipe suggestions for the 
		provided recipe.
		"""
		suggestion_recipe_lists = list()
		
		# Remove recipe from suggestion candidates list - extending a new list instead of deepcopy to avoid recursively 
		# recreating the Recipe objects
		primary_candidates_list = list()
		primary_candidates_list.extend(self.recipe_list)
		try:
			primary_candidates_list.remove(recipe)
		except ValueError:
			print(f"Could not find {recipe.title} in {self.name} collection")
			print(", ".join([r.title for r in primary_candidates_list]))
		finally:
			suggestion_recipe_lists.append(primary_candidates_list)

		suggestion_recipe_lists.extend([c.recipe_list for c in self.backup_collections])
		final_recipe_suggestions = list()

		for recipe_list in suggestion_recipe_lists:
			new_suggestions = random.sample(recipe_list, k=min(len(recipe_list), 10 - len(final_recipe_suggestions)))
			final_recipe_suggestions.extend(new_suggestions)

		suggestions_dynamo_records = list()

		for suggestion in final_recipe_suggestions:
			recipe_to_suggestion_mapping = {
				"PutRequest": {
					"Item": {
						"PK": {"S": recipe.recipe_id},
						"SK": {"S": f"SUGGESTS_RECIPE#{suggestion.id}"},
						"id": {"N": suggestion.id},
						"name": {"S": suggestion.title},
						"slug": {"S": suggestion.slug},
					}
				}
			}

			suggestion_to_recipe_mapping = {
				"PutRequest": {
					"Item": {
						"PK": {"S": suggestion.recipe_id},
						"SK": {"S": f"SUGGESTED_BY_RECIPE#{recipe.id}"},
						"id": {"N": recipe.id},
						"name": {"S": recipe.title},
						"slug": {"S": recipe.slug},
					}
				}
			}
			suggestions_dynamo_records.extend([recipe_to_suggestion_mapping, suggestion_to_recipe_mapping])

		return suggestions_dynamo_records






