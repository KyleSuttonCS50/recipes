import numpy as np
from cs50 import SQL
from bs4 import BeautifulSoup
import urllib.request
import os
import csv
from tempfile import mkdtemp

db = SQL("sqlite:///recipes.db")

clinks = []
chlinks = [[]]
recip_links = [[[]]]
ingredient = [[[[]]]]


# Get the categories
r = urllib.request.urlopen('http://www.bbc.co.uk/food/chefs').read()
soup = BeautifulSoup(r, "html.parser")
menu = soup.find("ol", class_="resource-nav")

categories = menu.find_all("li")

for category in categories:
    if category.a:
        cat_link = category.a["href"]
        clinks.append(cat_link)
    else:
        pass

i = 0

# Iterate over lists of chefs
for clink in clinks:
    s = urllib.request.urlopen('http://www.bbc.co.uk' + clink).read()
    ssoup = BeautifulSoup(s, "html.parser")

    # Find each chef
    ch = ssoup.find_all("li", class_="resource chef")
    chlinks.append([])
    ingredient.append([])
    recip_links.append([])
    for c in ch:
        chef_link = c.a["href"]
        chlinks[i].append(chef_link)
    j = 0

    # Iterate over chefs
    for chlink in chlinks[i]:
        t = urllib.request.urlopen('http://www.bbc.co.uk' + chlink).read()
        tsoup = BeautifulSoup(t, "html.parser")
        rls = tsoup.find("p", class_="see-more")
        if not rls:
            break

        # Make sure all your lists stay in range
        ingredient[i].append([])
        recip_links[i].append([])

        # Get link to the recipe list
        rl_link = rls.a["href"]
        u = urllib.request.urlopen('http://www.bbc.co.uk' + rl_link).read()
        rlink = rl_link
        usoup = BeautifulSoup(u, "html.parser")

        # Identify the number of results
        resultnum = usoup.find("div", class_="pagInfo-recipe-numbers")
        resulttxt = resultnum.get_text()
        resulttxt = resulttxt[9:]
        rsltnm = sum([int(it) for it in resulttxt.split() if it.isdigit()])
        divs = int(np.ceil(rsltnm / 15))

        k = 0

        # Find links to ALL the recipes
        for div in range(divs):
            v = urllib.request.urlopen('http://www.bbc.co.uk' + rlink).read()
            vsoup = BeautifulSoup(v, "html.parser")
            recips = vsoup.find_all("li", class_="article with-image")
            recips = recips + vsoup.find_all("li", class_="article no-image")

            # Get them links
            for recip in recips:
                recip_link = recip.div.h3.a["href"]
                recip_links[i][j].append(recip_link)

            # Deal with annoying results thing
            if div + 1 < divs:
                nextlink = vsoup.find("a", class_="see-all-search")
                rlink = nextlink["href"]
            else:
                pass

        # Iterate over recipes
        for reci_link in recip_links[i][j]:
            w = urllib.request.urlopen('http://www.bbc.co.uk' + reci_link).read()
            wsoup = BeautifulSoup(w, "html.parser")
            ings = wsoup.find_all("li", class_="recipe-ingredients__list-item")
            ingredient[i][j].append([])

            # Iterate over ingredients
            for ing in ings:
                if ing.a:
                    ing_link = ing.a["href"]

                    # Make the ingredients pretty
                    ingred = ing_link.replace("/food/", "")
                    ingred = ingred.replace("_", " ")

                    # Append them
                    ingredient[i][j][k].append(ingred + "\r")
                else:
                    pass

            # Name the recipes
            title = wsoup.find("h1", class_="content-title__text")
            name = title.get_text()
            print(name)

            # Give them a link
            link = 'http://www.bbc.co.uk' + reci_link

            # Insert info into database
            if ingredient[i][j][k] != None:
                ingredients = ''.join(str(e) for e in ingredient[i][j][k])
                insertion = db.execute("INSERT INTO recipes (name, ingredients, link) VALUES(:name, :ingredients, :link)",
                                       name=name, ingredients=ingredients, link=link)
                selection = db.execute("SELECT recipeid FROM recipes where name=:name", name=name)
                recipeid = selection[0]["recipeid"]
                for q in ingredient[i][j][k]:
                    ing_insert = db.execute("INSERT INTO ingredients (ingredient, recipeid) VALUES(:ingredient, :recipeid)",
                                            ingredient=q, recipeid=recipeid)
            k += 1

        j += 1

    i += 1
