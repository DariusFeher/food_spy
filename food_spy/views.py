from lib2to3.pgen2.literals import test
from tabnanny import verbose

from tesco_products.models import TescoProduct
from .tasks import send_notif_email
from background_task.models import Task
from nltk.stem import WordNetLemmatizer
import pickle

from django.shortcuts import render
from django.core.mail import send_mail
from tesco_products.tasks import update_tesco_products_db
from nltk import word_tokenize
import nltk

from gensim.parsing.preprocessing import remove_stopwords, strip_punctuation, strip_numeric, strip_non_alphanum, strip_multiple_whitespaces, strip_short
import re

import requests, lxml
import cloudscraper
from supermarkets_data.models import TescoData
import json
from tesco_products.utils import clean_mention

currencies = {
            '1' : '$',
            '2' : '€',
            '3' : '£',
}

def homePage(request):
    # if len(Task.objects.filter(verbose_name="send_notif_email")) == 0:
    #     send_notif_email(repeat=2, verbose_name="send_notif_email")
    # send_mail(
    #     'TEST EMAIL - REPETITIVE',
    #     'TEST MESSAGE...',
    #     'teamfoodspy@gmail.com',
    #     ['feherdarius7@gmail.com'],
    # )
    
    if len(Task.objects.filter(verbose_name="update_tesco_db")) == 0:
        update_tesco_products_db(repeat=Task.DAILY, verbose_name="update_tesco_db")

    if request.method == 'GET':
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

        print(clean_mention("Tesco Sweet Potatoes 1Kg"))
        return render(request, 'home.html')