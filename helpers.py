import numpy as np
from cs50 import SQL
from cs50 import get_string

def recipelist(ingredients):

    # Initialize some blank lists and variables
    names=[]
    appearances={}
    allrecipes=[]
    recipelist=[]
    ing_cur = 0

    # Looks up recipes that contain a given ingredient
    def lookup(ingredient):

        recipeids = []

        # Find recipes from the ingredients table
        ids = db.execute("""SELECT DISTINCT recipeid FROM ingredients WHERE
                        ingredient LIKE :ingredient OR ingredient LIKE :ingredient_2""",
                        ingredient=ingredient + "%", ingredient_2 = "%" + ingredient)

        # Add the recipe into the list if and only if it isn't already
        for id in ids:
            if not id["recipeid"] in recipeids:
                recipeids.append(id["recipeid"])

        # Keep track of the number of times each recipe appears in a dict
        for recipeid in recipeids:
            if not str(recipeid) in appearances:
                appearances[str(recipeid)] = 0
            appearances[str(recipeid)] = appearances[str(recipeid)] + 1

        return recipeids

    # Determines what percentage of the required ingredients you have
    def score(recipeid, ings):
        recipescore = appearances[str(recipeid)] / ings
        return recipescore

    # Use the right database
    db = SQL("sqlite:///recipes.db")

    # Look up the ingredients and append the recipes returned to a larger list
    for ingredient in ingredients:
        recipes = lookup(ingredient)
        for recipe in recipes:
            if not recipe in allrecipes:
                allrecipes.append(recipe)
        ing_cur += 1

    for arecipe in allrecipes:
        # Get the number of ingredients
        ingred = db.execute("SELECT ingredients FROM recipes WHERE recipeid=:recipeid", recipeid=arecipe)[0]["ingredients"]
        ings = 0
        for l in ingred.split("\r"):
            if l != "":
                ings += 1
        # Get each recipe's score
        recipescore = score(arecipe, ings)
        # Make a tuple
        recipetuple = (arecipe, recipescore)
        # Add to a list of tuples
        recipelist.append(recipetuple)

    # Sort the list by score
    recipelist.sort(key= lambda recipetuple : recipetuple[1], reverse=True)

    # Return the first ten elements
    return recipelist[:10]