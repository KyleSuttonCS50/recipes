from cs50 import SQL
from flask import Flask, flash, redirect, jsonify, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from bs4 import BeautifulSoup
import urllib.request
import inflection

# Get some helper functions
import helpers

# Configure application
app = Flask(__name__)

db = SQL("sqlite:///recipes.db")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Landing Page
@app.route("/", methods=["GET", "POST"])
def index():

    # After they submit the form
    if request.method == "POST":
        results = []
        k = 1
        # Get all of their ingredients
        while request.form.get('ingredient_'+ str(k)) != None:
            ingredient = request.form.get('ingredient_' + str(k))
            results.append(inflection.singularize(ingredient))
            k += 1
        recipes = helpers.recipelist(results)
        recipeinfo = []
        for recipetuple in recipes:
            recipeid = str(recipetuple[0])
            recipename = (db.execute("SELECT name FROM recipes WHERE recipeid=:recipeid", recipeid=recipeid))[0]["name"]
            recipescore = str(round((recipetuple[1] * 100), 1)) + '%'
            recipeinfo.append((recipeid, recipename, recipescore))
        return render_template("index.html", recipeinfo=recipeinfo)
    else:
        return render_template("ingredients.html")

@app.route("/recipe")
def getrecipe():
    steps = []
    ingredients = []
    recipe = {}
    recipeid = request.args.get("recipeid")
    recipelink = (db.execute("SELECT link FROM recipes WHERE recipeid=:recipeid", recipeid=recipeid))[0]["link"]
    r = urllib.request.urlopen(recipelink).read()
    rsoup = BeautifulSoup(r, "html.parser")
    recipe["recipename"] = rsoup.find("h1", class_="content-title__text").get_text()
    description = rsoup.find("p", class_="recipe-description__text")
    if description:
        recipe["description"] = description.get_text()
    recipe["author"] = rsoup.find("a", class_="chef__link").get_text()
    ingredientsoup = rsoup.find_all("li", class_="recipe-ingredients__list-item")
    servesoup = rsoup.find("p", class_="recipe-metadata__serving")
    if servesoup:
        recipe["serves"] = servesoup.get_text()
    for ingredient in ingredientsoup:
        ingredients.append(ingredient.get_text())
    recipe["ingredients"] = ingredients
    stepsoup = rsoup.find_all("p", class_="recipe-method__list-item-text")
    for step in stepsoup:
        steps.append(step.get_text())
    recipe["steps"] = steps
    recipe["link"] = recipelink
    return render_template("recipe.html", recipe = recipe)

