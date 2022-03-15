import concurrent.futures
from curses.ascii import HT
import json
from multiprocessing import context
import pickle
import re
import time
from email import message
from amazon_products.models import AmazonProduct
from amazon_products.tasks import update_amazon_products_db
from british_online_supermarket_products.models import BritishOnlineSupermarketProduct
from django.middleware import csrf

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


    return render(request, 'home.html', {})

def get_recipe_ingredients_prices(request):
    clean_session(request)
    if request.method == 'POST':
        if not request.session.exists(request.session.session_key):
            request.session.create()

        data = dict(request.POST)
        ingr_nr = data['ingredient_nr'][0]
        if ingr_nr == '1': # CLEAN PREVIOUS SAVED DATA
            request.session['tesco_products'] = {}
            request.session['british_online_supermarket_products'] = {}
            request.session['ingredients_list'] = []
        ingredient = str(data['ingredient_name'][0])
        request.session['ingredients_list'].append(ingredient)
        # print(data['list_of_ingredients'])
        print("INGR IS,,,,", ingredient)
        params = {
            'item' : '',
        }
        current_results_tesco = {}
        current_results_british_online_supermarket = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
                params['item'] = ingredient
                current_results_tesco[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/tesco', params).result()
                current_results_british_online_supermarket[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/britishOnlineSupermarket', params).result()
       
        request.session['tesco_products'][ingredient.title()] = current_results_tesco[ingredient.title()].json()
        request.session['british_online_supermarket_products'][ingredient.title()] = current_results_british_online_supermarket[ingredient.title()].json()       
        
        print(request.session['tesco_products'])
    return HttpResponse('Success')

@login_required(login_url='login')
def save_and_display_recipes(request):
    clean_session(request)
    id = None
    if request.method == 'POST':
        recipes = []
        if 'tesco_products' in request.session and 'british_online_supermarket_products' in request.session and request.session['tesco_products'] and request.session['british_online_supermarket_products']:
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

def clean_session(request):
    if 'new_tesco_products' in request.session:
        request.session['new_tesco_products'] = {}
    if 'new_british_online_supermarket_products' in request.session:
        request.session['new_british_online_supermarket_products'] = {}

@login_required(login_url='login')
def display_my_recipes(request, id):
    clean_session(request)
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
        if 'new_tesco_products' in request.session and request.session['new_tesco_products']:
            context['display_recipe_comparison_button'] = False
        else:
            context['display_recipe_comparison_button'] = True
        context['last_updated'] = recipe.last_updated.strftime("%d %B %Y at %I:%M %p")
        if 'new_tesco_products' in request.session:
            context['new_tesco_products'] = request.session['new_tesco_products']
        if 'new_british_online_supermarket_products' in request.session:
            context['new_british_online_supermarket_products'] = request.session['new_british_online_supermarket_products']
        request.session['recipe_id'] = pk
        request.session['ingredients'] = json.dumps(list(recipe.products_tesco.keys()))
        print(request.session['ingredients'])

        if request.method == 'POST':
            if not request.session.exists(request.session.session_key):
                request.session.create()

            data = dict(request.POST)
            print(data)
            ingr_nr = data['ingredient_nr'][0]
            if ingr_nr == '1': # CLEAN PREVIOUS SAVED DATA
                request.session['new_tesco_products'] = {}
                request.session['new_british_online_supermarket_products'] = {}
            ingredient = str(data['ingredient_name'][0])
            # print(data['list_of_ingredients'])
            print("INGR IS,,,,", ingredient)
            params = {
                'item' : '',
            }
            current_results_tesco = {}
            current_results_british_online_supermarket = {}
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                    params['item'] = ingredient
                    current_results_tesco[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/tesco', params).result()
                    current_results_british_online_supermarket[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/britishOnlineSupermarket', params).result()
        
            request.session['new_tesco_products'][ingredient.title()] = current_results_tesco[ingredient.title()].json()
            request.session['new_british_online_supermarket_products'][ingredient.title()] = current_results_british_online_supermarket[ingredient.title()].json()     
            print("ingr NR:", ingr_nr)
            print(len(request.session['ingredients']))  
            if int(ingr_nr) == len(list(recipe.products_tesco.keys())):
                print('last one')
                recipe = Recipe(
                    user = request.user,
                    pk=pk,
                    products_tesco = request.session['new_tesco_products'],
                    products_british_online_supermarket = request.session['new_british_online_supermarket_products']
                )
                recipe.save()
                context['display_recipe_comparison_button'] = False
                context['new_tesco_products'] = request.session['new_tesco_products']
                context['new_british_online_supermarket_products'] = request.session['new_british_online_supermarket_products']
                if request.session['new_tesco_products'] != tesco_products or request.session['new_british_online_supermarket_products'] != british_online_supermarket_products:
                    print("DIFFERENT")
                else:
                    messages.info(request, "The prices have not been changed since the last time!")
        # if request.method == 'POST':
        #     results = {}
        #     ingredients = recipe.products_tesco.keys()
        #     params = {
        #         'item' : '',
        #     }
        #     results_tesco = {}
        #     results_british_online_supermarket = {}
        #     for ingredient in ingredients:
        #         params['item'] = ingredient

        #         with concurrent.futures.ThreadPoolExecutor() as executor:
        #                 results_tesco[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/tesco', params).result()
        #                 results_british_online_supermarket[ingredient.title()] = executor.submit(requests.get, 'http://food-price-compare-api-dlzhh.ondigitalocean.app/api/food/britishOnlineSupermarket', params).result()

        #     for res in results_tesco:
        #         results_tesco[res] = results_tesco[res].json()

        #     for res in results_british_online_supermarket:
        #         results_british_online_supermarket[res] = results_british_online_supermarket[res].json()
                
        #     # print(results)
        #     context['new_tesco_products'] = results_tesco
        #     context['new_british_online_supermarket_products'] = results_british_online_supermarket
        #     if results_tesco != tesco_products or results_british_online_supermarket != british_online_supermarket_products:
        #         print("DIFFERENT")
        #     else:
        #         messages.info(request, "The prices have not been changed since the last time!")
            
        #     recipe = Recipe(
        #         user = request.user,
        #         pk=pk,
        #         products_tesco = results_tesco,
        #         products_british_online_supermarket = results_british_online_supermarket
        #     )
        #     recipe.save()
        #     context['display_recipe_comparison_button'] = False
    return render(request, 'recipe_prices_comparison.html', context)

@login_required(login_url='login')
def deleteRecipe(request, pk):
    print(pk)
    recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
    recipe.delete()
    messages.success(request, ("Recipe has been deleted successfully!"))
    return redirect('/myrecipes/')
