import concurrent.futures
import json
import pickle
import re
import time
from email import message
from amazon_products.tasks import update_amazon_products_db

import cloudscraper
import lxml
import nltk
import requests
from background_task.models import Task
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from gensim.parsing.preprocessing import (remove_stopwords,
                                          strip_multiple_whitespaces,
                                          strip_non_alphanum, strip_numeric,
                                          strip_punctuation, strip_short)
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from recipes.models import Recipe
from supermarkets_data.models import TescoData
from tesco_products.models import TescoProduct
from tesco_products.tasks import update_tesco_products_db
from amazon_products.tasks import update_amazon_products_db
from tesco_products.utils import clean_mention
from bs4 import BeautifulSoup

currencies = {
            '1' : '$',
            '2' : '€',
            '3' : '£',
}

def homePage(request):
    if len(Task.objects.filter(verbose_name="update_tesco_db")) == 0:
        update_tesco_products_db(repeat=Task.DAILY, verbose_name="update_tesco_db")

    if len(Task.objects.filter(verbose_name="update_amazon_db")) == 0:
        update_amazon_products_db(repeat=Task.DAILY, verbose_name="update_amazon_db")
    # headers = {'User-agent':
    # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
    #     'Accept': '*/*',
    #     'Cache-Control': 'no-cache',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Connection': 'keep-alive',
    #     'Cookie': 'bm_sz=04919BE521C5C4D8ADF4617D5250A484~YAAQrpxkX+b8IYVyAQAA/VQr0QgTg5gDEXUmuUfa0qqtHv0QHHZjtL4gcSJ9RA7hoaEXJOTp1DYPb9xCrGwP37BrvtUY2kCKB7PqvVLXAXnfrt9F0ZiEPj10SiSVXZRZj8klW46ZA7Ho/0XtWlsO2aFX1MPkmD2/C10cDH6E1PgeO9EUNkZi9uPu109p4DE=; _abck=5621BD87FE69A39458BD0AB267BB9A81~-1~YAAQrpxkX+f8IYVyAQAA/VQr0QTSvxcBlxnRsND9THtPksH0EbfK/A3XkW0xT9oCk0Bj1ewbVDXr3PqtBjR7hHO6h6IXMvC2XID5RrAk0gVEKGwm9RDyBWyvp6hnPzicHMH6tTUIZdYLmssjIBAJ2WnpBkKUuF0YbX45V4H8d3m6u8FOhyqZewFyT1+Yvh14NDHwmDw4Yb4hQkLPglrkzt8LV39SpfSjjGkWMjyX4l967aCe+SHK5hjcTIz9bjSAoOQNqFWR5ATMnfBDSLOfaAQ4Dic=~-1~-1~-1; atrc=48693e75-78d9-4fce-85d0-9a0a50232644; _csrf=2wH2UKiamS-tjvd4hERekcG2',
    #     'Referer': 'https://www.amazon.com/'
    #     }
    # params = {
    #     'page' : 1,

    # }
    if 'tesco_products' in request.session and request.session['tesco_products']:
        products = request.session['tesco_products']
        return render(request, 'home.html', {'products' : products})
    return render(request, 'home.html')
    # elif request.method == 'POST':
    #     print(request.POST)
    #     return render(request, 'home.html')

def get_recipe_ingredients_prices(request):
    results = {}
    if request.method == 'POST':
        data = dict(request.POST)
        if 'ingredients' in data:
            ingredients = data['ingredients']
            params = {
                'item' : '',
            }
            
            print("CALLING API!")
            print(ingredients)
            for ingredient in ingredients:
                params['item'] = ingredient
                print(ingredient)
                print(params)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                        results[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food', params).result()
                # results[ingredient.title()] = pool.apply_async(requests.get, ['http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food'], {'params' : params}).get().json()
            # print("JUST FINISHED!")
            print(len(results))
            print(results)
            request.session['tesco_products'] = {}
            for res in results:
                results[res] = results[res].json()
                print(str(res))
                print(results[res])
                
            print(results)
            request.session['tesco_products'] = results
        else:
             return render(request, 'home.html', {'products' : results, 'infoMessage': 'Please enter at least an ingredient!'})

    return render(request, 'home.html', {'products' : results})

@login_required(login_url='login')
def save_and_display_recipes(request):
    id = None
    if request.method == 'POST':
        recipes = Recipe.objects.filter(user=request.user,
                                        products_tesco=request.session['tesco_products'],
                                        products_amazon=request.session['tesco_products'])
        if len(recipes) == 0:
            recipe = Recipe(
                user = request.user,
                products_tesco = request.session['tesco_products'],
                products_amazon = request.session['tesco_products']
            )
            recipe.save()
            messages.success(request, "Recipe saved successfully!")
        else:
            id = recipes[0].pk
            # messages.warning(request, msg)
    return display_my_recipes(request, id)

@login_required(login_url='login')
def display_my_recipes(request, id):
    all_recipes = list(Recipe.objects.filter(user=request.user).order_by('-last_updated'))
    recipes = [] # List of all user's recipes
    # For each recipe we need to store: id, tesco_products (list), amazon_products
    # For each product in list we need: ingredients
    # E.g.:
    # recipes = [
    #     {
    #         'id': 1,
    #         'products_tesco' : [
    #             {
    #                 'ingredient' : tomato,
    #                 'price': £1.45,
    #                 'link': https//tesco.com//groceries/en-GB/222739110,
    #             }
    #         ]
    #     }
    counter = 1
    for recipe in all_recipes:
        new_recipe = {}
        new_recipe['id'] = recipe.pk
        if id and recipe.pk == id:
            messages.warning(request, "You already saved this recipe, namely Recipe " + str(counter) + "!")
        new_recipe['last_updated'] = recipe.last_updated.strftime("%d %B %Y at %I:%M %p")
        new_recipe['products'] = []
        for ingredient in recipe.products_tesco:
            product = {}
            product['ingredient'] = ingredient
            product['price_tesco'] = str(recipe.products_tesco[ingredient][0]['price']) + str(recipe.products_tesco[ingredient][0]['currency'])
            product['link_tesco'] = str(recipe.products_tesco[ingredient][0]['link'])
            new_recipe['products'].append(product)
        recipes.append(new_recipe)
        counter += 1

    paginator = Paginator(recipes, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'my_recipes.html', {'page_obj': page_obj,
                                               'recipes' : recipes,
                                               'range': range(1, page_obj.paginator.num_pages + 1)})

@login_required(login_url='login')
def recipe_price_comparison(request, pk):
    context = {}
    recipe = Recipe.objects.get(user=request.user, pk=pk)
    context['recipe_id'] = pk
    if recipe:
        tesco_products = recipe.products_tesco
        amazon_products = recipe.products_amazon
        context['tesco_products'] = tesco_products
        context['amazon_products'] = amazon_products
        context['display_recipe_comparison_button'] = True
        context['last_updated'] = recipe.last_updated.strftime("%d %B %Y at %I:%M %p")
        if request.method == 'POST':
            results = {}
            ingredients = recipe.products_tesco.keys()
            # print(ingredients)
            params = {
                'item' : '',
            }
            # print("CALLING API!")
            # print(ingredients)
            for ingredient in ingredients:
                params['item'] = ingredient
                # print(ingredient)
                # print(params)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                        results[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food', params).result()
                # results[ingredient.title()] = pool.apply_async(requests.get, ['http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food'], {'params' : params}).get().json()
            # print("JUST FINISHED!")
            # print(len(results))
            # print(results)
            exist_changes = False
            ingredients_updated = []
            for res in results:
                results[res] = results[res].json()
                # print(str(res))
                # print(results[res])
                
            # print(results)
            context['new_tesco_products'] = results
            context['new_amazon_products'] = results
            if results != tesco_products:
                print("DIFFERENT")
            else:
                messages.info(request, "The prices have not been changed since the last time!")
                print("SAME")
            recipe = Recipe(
                user = request.user,
                pk=pk,
                products_tesco = results,
                products_amazon = results
            )
            recipe.save()
            context['display_recipe_comparison_button'] = False
    return render(request, 'recipe_prices_comparison.html', context)

# @login_required(login_url='login')
# def recipe_price_comparison(request, pk):
#     context = {}
#     recipe = Recipe.objects.get(user=request.user, pk=pk)
#     if recipe:
#         tesco_products = recipe.products_tesco
#         amazon_products = recipe.products_amazon
#         context['tesco_products'] = tesco_products
#         context['amazon_products'] = amazon_products
#         context['last_updated'] = recipe.last_updated
#     return render(request, 'recipe_prices_comparison.html', context)

@login_required(login_url='login')
def deleteRecipe(request, pk):
    print(pk)
    recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
    recipe.delete()
    messages.success(request, ("Recipe has been deleted successfully!"))
    return redirect('/myrecipes')
