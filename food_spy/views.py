import concurrent.futures
import json
import pickle
import re
from email import message

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
from tesco_products.utils import clean_mention

currencies = {
            '1' : '$',
            '2' : '€',
            '3' : '£',
}

def homePage(request):
    print("HERE")
    # if len(Task.objects.filter(verbose_name="send_notif_email")) == 0:
    #     send_notif_email(repeat=2, verbose_name="send_notif_email")
    # send_mail(
    #     'TEST EMAIL - REPETITIVE',
    #     'TEST MESSAGE...',
    #     'teamfoodspy@gmail.com',
    #     ['feherdarius7@gmail.com'],
    # )
    # for item in request.GET.items():
    #     print(item)
  
    if len(Task.objects.filter(verbose_name="update_tesco_db")) == 0:
        update_tesco_products_db(repeat=Task.DAILY, verbose_name="update_tesco_db")

    # if request.method == 'GET':
        # print("START REQUEST HOMEPAGE")
        # category_urls = {
        #     'fresh-food' : 'https://www.tesco.com/groceries/en-GB/shop/fresh-food/all?include-children=true',
        #     'bakery' : 'https://www.tesco.com/groceries/en-GB/shop/bakery/all',
        #     'frozen-food' : 'https://www.tesco.com/groceries/en-GB/shop/frozen-food/all',
        #     'food-cupboard' : 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all',
        #     'drinks' : 'https://www.tesco.com/groceries/en-GB/shop/drinks/all',
        #     'easter' : 'https://www.tesco.com/groceries/en-GB/shop/easter/all',
        #     'pet-food' : 'https://www.tesco.com/groceries/en-GB/shop/pets/all',
        # }
        # headers = {
        #     'User-agent':
        #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        # }

        # params = {
        #     'page' : 1
        # }
        # scraper = cloudscraper.create_scraper()
        # html = scraper.get('https://www.tesco.com/groceries/en-GB/shop/fresh-food/all?include-children=true', headers=headers, params=params).text
        # print("END REQUEST HOMPAGE")
        # print(html[:100])

        # tesco_products = TescoProduct.objects.all()
        # entities = {}
        # protected_tokens = set()
        # for product in tesco_products:
        #     cleaned_entity= clean_mention(product.short_name)
        #     if cleaned_entity not in entities:
        #         entities[cleaned_entity] = []
        #     new_prod = {}
        #     new_prod['short_name'] = product.short_name
        #     new_prod['price'] = product.price
        #     new_prod['currency'] = currencies[product.currency]
        #     new_prod['full_name'] = product.full_name
        #     new_prod['link'] = product.link
        #     new_prod['cleaned_short_name'] = cleaned_entity
        #     new_prod['cleaned_full_name'] = clean_mention(product.full_name)
        #     new_prod['id'] = product.id
        #     entities[cleaned_entity].append(new_prod)
        #     text = nltk.word_tokenize(new_prod['cleaned_short_name'])
        #     tags = nltk.pos_tag(text, tagset='universal')
        #     for tag in tags:
        #         if tag[1] == 'NOUN':
        #             protected_tokens.add(tag[0])
        #     text = nltk.word_tokenize(new_prod['cleaned_full_name'])
        #     tags = nltk.pos_tag(text, tagset='universal')
        #     if 'Tamarind' in product.full_name:
        #         print(product.full_name)
        #         print(tags)
        #     for tag in tags:
                
        #         if tag[1] == 'NOUN':
        #             protected_tokens.add(tag[0])

        # print(len(entities))
        # print(len(protected_tokens))

        # pickle.dump(entities, open("/Users/dariusmarianfeher/Documents/ThirdYearProject/tesco_kb_data.pickle", "wb"))
        # pickle.dump(protected_tokens, open("/Users/dariusmarianfeher/Documents/ThirdYearProject/tesco_protected_tokens.pickle", "wb"))
        # entities = pickle.load(open("/Users/dariusmarianfeher/Documents/ThirdYearProject/tesco_kb_data.pickle", "rb"))
        # protected_tokens = pickle.load(open("/Users/dariusmarianfeher/Documents/ThirdYearProject/tesco_protected_tokens.pickle", "rb"))
        # tescoData = TescoData(
        #     protected_tokens = protected_tokens,
        #     products_data = entities,
        # )
        # print(len(entities))
        # # tescoData.save()
        # tescoDataObj = TescoData.objects.all()[0]
        # # # print(len(objects))
        # # protected_tokens = objects.protected_tokens
        # # entities = objects.products_data
        # # print(len(protected_tokens))
        # tescoDataObj.delete()
        
        # # pickle.dump(test_list, open("test_list.pickle", "wb"))
        # # pickle.dump(test_list2, open("test_list2.pickle", "wb"))
        # # file = pickle.load(open("test_list.pickle", "rb"))
        # # file2 = pickle.load(open("test_list2.pickle", "rb"))
        
        # tescoDataObj = TescoData.objects.all()
        # if tescoDataObj:
        #     tescoDataObj = tescoDataObj[0]
        #     # print(len(objects))
        #     protected_tokens = set(tescoDataObj.protected_tokens)
        #     entities = tescoDataObj.products_data
        #     print(protected_tokens)
        #     print(entities)
        
        # test_list = [1, 2, 3, 4, 5]
        # test_list2 = [1, 2, 3]
        # jsonStr = json.dumps(test_list)
        # jsonStr2 = json.dumps(test_list2)
        # tescoData = TescoData(
        #     protected_tokens = jsonStr,
        #     products_data = jsonStr2,
        # )
        # tescoData.save()

        # print(clean_mention("Tesco Sweet Potatoes 1Kg"))
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
            request.session['test2'] = 'just testing'
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
    print("PRICE COMPARISON METHOD")
    print(pk)
    return render(request, 'recipe_prices_comparison.html')

@login_required(login_url='login')
def deleteRecipe(request, pk):
    print(pk)
    recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
    recipe.delete()
    messages.success(request, ("Recipe has been deleted successfully!"))
    return redirect('/myrecipes')
