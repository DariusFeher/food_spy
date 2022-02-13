import pickle
import time

import cloudscraper
import lxml
import nltk
import requests
from supermarkets_data.models import AmazonData
from background_task import background
from bs4 import BeautifulSoup
from tesco_products.utils import clean_mention
import re

from .models import AmazonProduct

currencies = {
            '$' : '1',
            '€' : '2',
            '£' : '3',
}

headers = {'User-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': 'bm_sz=04919BE521C5C4D8ADF4617D5250A484~YAAQrpxkX+b8IYVyAQAA/VQr0QgTg5gDEXUmuUfa0qqtHv0QHHZjtL4gcSJ9RA7hoaEXJOTp1DYPb9xCrGwP37BrvtUY2kCKB7PqvVLXAXnfrt9F0ZiEPj10SiSVXZRZj8klW46ZA7Ho/0XtWlsO2aFX1MPkmD2/C10cDH6E1PgeO9EUNkZi9uPu109p4DE=; _abck=5621BD87FE69A39458BD0AB267BB9A81~-1~YAAQrpxkX+f8IYVyAQAA/VQr0QTSvxcBlxnRsND9THtPksH0EbfK/A3XkW0xT9oCk0Bj1ewbVDXr3PqtBjR7hHO6h6IXMvC2XID5RrAk0gVEKGwm9RDyBWyvp6hnPzicHMH6tTUIZdYLmssjIBAJ2WnpBkKUuF0YbX45V4H8d3m6u8FOhyqZewFyT1+Yvh14NDHwmDw4Yb4hQkLPglrkzt8LV39SpfSjjGkWMjyX4l967aCe+SHK5hjcTIz9bjSAoOQNqFWR5ATMnfBDSLOfaAQ4Dic=~-1~-1~-1; atrc=48693e75-78d9-4fce-85d0-9a0a50232644; _csrf=2wH2UKiamS-tjvd4hERekcG2',
        'Referer': 'http://www.amazon.com/'
        }
BASE_URL = 'https://www.amazon.co.uk/'

params = {
	'page' : 1,
}

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('wordnet')

@background()
def update_amazon_products_db():
    entities = {}
    protected_tokens = set()
    ids = set()
    retries = 0
    while True:
        scraper = cloudscraper.create_scraper()
        html = scraper.get('https://www.amazon.co.uk/s?i=grocery&bbn=6723205031', headers=headers, params=params).text
        time.sleep(1.0)
        if "Try checking your spelling or use more general terms" in html:
            break
        soup = BeautifulSoup(html, 'html.parser')
        try:
            prodList = soup.findAll('div', {'class' : 'a-section a-spacing-base'})
        except:
            break
        no_prod = 0
        for product in prodList:
            try:
                full_name = product.find('span', {'class' : "a-size-base-plus a-color-base a-text-normal"}).text
                price = product.find('span', {'class' : "a-price-whole"}).text + product.find('span', {'class' : "a-price-fraction"}).text
                currency = product.find('span', {'class' : "a-price-symbol"}).text
                link = BASE_URL + product.find('a', {'class' : 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})['href']
                id_product =  re.search(r'/dp/(.*?)/', link).group(1)
            except:
                print('Error')
                continue
            
            try:
                amazonProduct = AmazonProduct.objects.get(id=id_product) 
            except:
                amazonProduct = None
            if amazonProduct:
                amazonProduct.price = price
                amazonProduct.currency = currencies[currency]
                amazonProduct.link = link
                amazonProduct.full_name = full_name
                amazonProduct.save()
            else:
                product = AmazonProduct(
                    price = price,
                    currency = currencies[currency],
                    link = link,
                    full_name = full_name,
                    id = id_product
                )
                product.save()
            no_prod += 1
            ids.add(id_product)

            # print("PAGE", params['page'])
            # print("PRODUCTS:", no_prod)

            cleaned_entity= clean_mention(product.full_name)
            if cleaned_entity not in entities:
                entities[cleaned_entity] = []
                new_prod = {}
                new_prod['price'] = product.price
                new_prod['currency'] = currency
                new_prod['full_name'] = product.full_name
                new_prod['link'] = product.link
                new_prod['cleaned_full_name'] = cleaned_entity
                new_prod['id'] = product.id
                entities[cleaned_entity].append(new_prod)
            
                text = nltk.word_tokenize(new_prod['cleaned_full_name'])
                tags = nltk.pos_tag(text, tagset='universal')
                
                for tag in tags:
                    if tag[1] == 'NOUN':
                        protected_tokens.add(tag[0])

        if no_prod or retries == 100:
            # print(soup.prettify())
            params['page'] += 1
            retries = 0
        else:
            retries += 1
            # print("RETRYING")
        # print('----------')
    # Delete last lists of entities and protected tokens            
    amazonDataObj = AmazonData.objects.all()
    if len(amazonDataObj) > 0:
        amazonDataObj = amazonDataObj[0]
        amazonDataObj.delete()

    # Replace them with the updated ones
    amazonDataObj = AmazonData(
        products_data = entities,
        protected_tokens = list(protected_tokens)
    )
    amazonDataObj.save()

    # Delete the products which are not part of Amazon's offer
    amazonProducts = AmazonProduct.objects.all()
    for product in amazonProducts: 
        if product.id not in ids:
            product.delete()
