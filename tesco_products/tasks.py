from bs4 import BeautifulSoup
import requests, lxml
import time
from .models import TescoProduct
from background_task import background

params = {
	'page' : 1
}

BASE_URL = 'https://www.tesco.com'

category_urls = {
	'fresh-food' : 'https://www.tesco.com/groceries/en-GB/shop/fresh-food/all?include-children=true',
	'bakery' : 'https://www.tesco.com/groceries/en-GB/shop/bakery/all',
	'frozen-food' : 'https://www.tesco.com/groceries/en-GB/shop/frozen-food/all',
	'food-cupboard' : 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all',
	'drinks' : 'https://www.tesco.com/groceries/en-GB/shop/drinks/all',
	'easter' : 'https://www.tesco.com/groceries/en-GB/shop/easter/all',
	'pet-food' : 'https://www.tesco.com/groceries/en-GB/shop/pets/all',
}

headers = {'User-Agent': 'PostmanRuntime/7.25.0',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Host': 'www.tesco.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': 'bm_sz=04919BE521C5C4D8ADF4617D5250A484~YAAQrpxkX+b8IYVyAQAA/VQr0QgTg5gDEXUmuUfa0qqtHv0QHHZjtL4gcSJ9RA7hoaEXJOTp1DYPb9xCrGwP37BrvtUY2kCKB7PqvVLXAXnfrt9F0ZiEPj10SiSVXZRZj8klW46ZA7Ho/0XtWlsO2aFX1MPkmD2/C10cDH6E1PgeO9EUNkZi9uPu109p4DE=; _abck=5621BD87FE69A39458BD0AB267BB9A81~-1~YAAQrpxkX+f8IYVyAQAA/VQr0QTSvxcBlxnRsND9THtPksH0EbfK/A3XkW0xT9oCk0Bj1ewbVDXr3PqtBjR7hHO6h6IXMvC2XID5RrAk0gVEKGwm9RDyBWyvp6hnPzicHMH6tTUIZdYLmssjIBAJ2WnpBkKUuF0YbX45V4H8d3m6u8FOhyqZewFyT1+Yvh14NDHwmDw4Yb4hQkLPglrkzt8LV39SpfSjjGkWMjyX4l967aCe+SHK5hjcTIz9bjSAoOQNqFWR5ATMnfBDSLOfaAQ4Dic=~-1~-1~-1; atrc=48693e75-78d9-4fce-85d0-9a0a50232644; _csrf=2wH2UKiamS-tjvd4hERekcG2',
        'Referer': 'http://www.tesco.com/'
        }

currencies = {
            '$' : '1',
            '€' : '2',
            '£' : '3',
}

@background
def update_tesco_products_db():
    for category in category_urls:
        params['page'] = 1 # Restart page nr
        retries = 0
        while True:
            print("START REQUEST")
            html = requests.get(category_urls[category], headers=headers, params=params).text
            print("END REQUEST")
            time.sleep(0.5)
            if "the page you are looking for has not been found" in html:
                break
            soup = BeautifulSoup(html, 'html.parser')
            try:
                prodList = soup.find('div', {'class':'product-lists'}).find('ul').findAll('li', {'class': 'product-list--list-item'})
            except:
                break
            print("PAGE", params['page'])
            no_prod = 0
            for product in prodList:
                prod = None
                price = None
                currency = None

                try:
                    short_name = product.find('span', {'class' : "visually-hidden"}).text
                    price = product.find('span', {'class' : "value"}).text
                    currency = product.find('span', {'class' : "currency"}).text
                    link = BASE_URL + product.find('a', {'class' : 'eYySMn'})['href']
                    full_name = product.find('a', {'class' : 'eYySMn'}).text
                    id_product = str(product.find('input', {'name' : "id"})['value'])
                except:
                    continue
                
                try:
                    tescoProduct = TescoProduct.objects.get_(id=id_product) 
                except:
                    tescoProduct = None
                if tescoProduct:
                    tescoProduct.short_name = short_name
                    tescoProduct.price = price
                    tescoProduct.currency = currencies[currency]
                    tescoProduct.link = link
                    tescoProduct.full_name = full_name
                    tescoProduct.save()
                else:
                    product = TescoProduct(
                    short_name = short_name,
                    price = price,
                    currency = currencies[currency],
                    link = link,
                    full_name = full_name,
                    id = id_product
                    )
                    product.save()
                no_prod += 1


            print("PRODUCTS:", no_prod)
            print('----------')
            if no_prod or retries == 100:
                params['page'] += 1
                retries = 0
            else:
                retries += 1

