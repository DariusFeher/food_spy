import concurrent.futures
import json
from multiprocessing import context
import pickle
import re
import time
from email import message
from amazon_products.models import AmazonProduct
from amazon_products.tasks import update_amazon_products_db
from british_online_supermarket_products.models import BritishOnlineSupermarketProduct

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
from supermarkets_data.models import AmazonData, BritishOnlineSupermarketData, TescoData
from tesco_products.models import TescoProduct
from tesco_products.tasks import update_tesco_products_db
from amazon_products.tasks import update_amazon_products_db
from sainsburys_products.tasks import update_sainsburys_products_db
from british_online_supermarket_products.tasks import update_britishOnlineSupermarket_products_db
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

    if len(Task.objects.filter(verbose_name="update_britishOnlineSupermarket_db")) == 0:
        update_britishOnlineSupermarket_products_db(repeat=Task.DAILY, verbose_name="update_britishOnlineSupermarket_db")

    # if len(Task.objects.filter(verbose_name="update_amazon_db")) == 0:
    #     update_amazon_products_db(repeat=Task.DAILY, verbose_name="update_amazon_db")

    # if len(Task.objects.filter(verbose_name="update_sainsburys_db")) == 0:
    #     update_sainsburys_products_db(repeat=Task.DAILY, verbose_name="update_sainsburys_db")
    
    # tesco_products = BritishOnlineSupermarketProduct.objects.all()
    # entities = {}
    # protected_tokens = set()
    # ids = set()
    # entities_with_ids = {}
    # for product in tesco_products:
    #     cleaned_entity= clean_mention(product.full_name)
    #     new_prod = {}
    #     new_prod['price'] = product.price
    #     new_prod['currency'] = currencies[product.currency]
    #     new_prod['full_name'] = product.full_name
    #     new_prod['link'] = product.link
    #     new_prod['cleaned_full_name'] = cleaned_entity
    #     new_prod['id'] = product.id
    #     entities[product.id] = new_prod
        
    #     ids.add(product.id)

    #     if cleaned_entity not in entities_with_ids:
    #         entities_with_ids[cleaned_entity] = []
    #     entities_with_ids[cleaned_entity].append(new_prod['id'])

    #     text = nltk.word_tokenize(new_prod['cleaned_full_name'])
    #     tags = nltk.pos_tag(text, tagset='universal')
    #     for tag in tags:
    #         if tag[1] == 'NOUN':
    #             protected_tokens.add(tag[0])
    # cnt = 0
    # for ent in entities_with_ids:
    #     for id in entities_with_ids[ent]:
    #         cnt += 1
    
    # print(len(entities))
    # print(len(protected_tokens)) 
    # print(len(ids))
    # print(list(ids)[:5])
    # print("CNT IS:", cnt)
    # tescoData = BritishOnlineSupermarketData(
    #         protected_tokens = list(protected_tokens),
    #         products_data = entities,
    #         products_entities = entities_with_ids,
    #     )
    # tescoData.save()
    context = {}
    if 'ingredients' in request.session and request.session['ingredients']:
        context['ingredients'] = request.session['ingredients']
    else:
        context['ingredients'] = []
    if 'tesco_products' in request.session and request.session['tesco_products']:
        context['tesco_products'] = request.session['tesco_products']
    else:
       context['tesco_products'] = []
    if 'british_online_supermarket_products' in request.session and request.session['british_online_supermarket_products']:
        context['british_online_supermarket_products'] = request.session['british_online_supermarket_products']
    else:
        context['british_online_supermarket_products'] = []

    return render(request, 'home.html', context)

def get_recipe_ingredients_prices(request):
    results_tesco = {}
    results_british_online_supermarket = {}
    context = {}
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
                        results_tesco[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/tesco', params).result()
                        results_british_online_supermarket[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/britishOnlineSupermarket', params).result()
                # results_tesco[ingredient.title()] = pool.apply_async(requests.get, ['http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food'], {'params' : params}).get().json()
            # print("JUST FINISHED!")
            print(len(results_tesco))
            print(len(results_british_online_supermarket))
            print(results_tesco)
            request.session['tesco_products'] = {}
            for res in results_tesco:
                results_tesco[res] = results_tesco[res].json()
                print(str(res))
                print(results_tesco[res])

            for res in results_british_online_supermarket:
                results_british_online_supermarket[res] = results_british_online_supermarket[res].json()
                print(str(res))
                print(results_british_online_supermarket[res])
                
            # print(results_tesco)
            request.session['ingredients'] = ingredients
            request.session['tesco_products'] = results_tesco
            request.session['british_online_supermarket_products'] = results_british_online_supermarket
        else:
            context['infoMessage'] =  'Please enter at least an ingredient!'

    if 'ingredients' in request.session and request.session['ingredients']:
        context['ingredients'] = request.session['ingredients']
    else:
        context['ingredients'] = []
    if 'tesco_products' in request.session and request.session['tesco_products']:
        context['tesco_products'] = request.session['tesco_products']
    else:
        context['tesco_products'] = []
    if 'british_online_supermarket_products' in request.session and request.session['british_online_supermarket_products']:
        context['british_online_supermarket_products'] = request.session['british_online_supermarket_products']
    else:
        context['british_online_supermarket_products'] = []

    return render(request, 'home.html', context)

@login_required(login_url='login')
def save_and_display_recipes(request):
    id = None
    if request.method == 'POST':
        recipes = []
        if request.session['tesco_products'] and request.session['british_online_supermarket_products']:
            recipes = Recipe.objects.filter(user=request.user,
                                            products_tesco=request.session['tesco_products'],
                                            products_british_online_supermarket=request.session['british_online_supermarket_products'])
        if len(recipes) == 0:
            recipe = Recipe(
                user = request.user,
                products_tesco = request.session['tesco_products'],
                products_british_online_supermarket = request.session['british_online_supermarket_products']
            )
            recipe.save()
            messages.success(request, "Recipe saved successfully!")
        else:
            id = recipes[0].pk
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
            product['price_british_online_supermarket'] = str(recipe.products_british_online_supermarket[ingredient][0]['price']) + str(recipe.products_british_online_supermarket[ingredient][0]['currency'])
            product['link_british_online_supermarket'] = str(recipe.products_british_online_supermarket[ingredient][0]['link'])
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
        british_online_supermarket_products = recipe.products_british_online_supermarket
        context['tesco_products'] = tesco_products
        context['british_online_supermarket_products'] = british_online_supermarket_products
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
            results_tesco = {}
            results_british_online_supermarket = {}
            for ingredient in ingredients:
                params['item'] = ingredient
                # print(ingredient)
                # print(params)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                        results_tesco[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/tesco', params).result()
                        results_british_online_supermarket[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/britishOnlineSupermarket', params).result()

            for res in results_tesco:
                results_tesco[res] = results_tesco[res].json()

            for res in results_british_online_supermarket:
                results_british_online_supermarket[res] = results_british_online_supermarket[res].json()
                
            # print(results)
            context['new_tesco_products'] = results_tesco
            context['new_british_online_supermarket_products'] = results_british_online_supermarket
            if results_tesco != tesco_products or results_british_online_supermarket != british_online_supermarket_products:
                print("DIFFERENT")
            else:
                messages.info(request, "The prices have not been changed since the last time!")
            
            recipe = Recipe(
                user = request.user,
                pk=pk,
                products_tesco = results_tesco,
                products_british_online_supermarket = results_british_online_supermarket
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
