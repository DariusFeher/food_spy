from bs4 import BeautifulSoup
import requests, lxml
import time
from .models import TescoProduct
from background_task import background


headers = {
    'User-agent':
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
  }

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
            html = requests.get(category_urls[category], headers=headers, params=params).text
            time.sleep(0.5)
            if "the page you are looking for has not been found" in html:
                break
            soup = BeautifulSoup(html, 'html.parser')
            try:
                prodList = soup.find('div', {'class':'product-lists'}).find('ul').findAll('li', {'class': 'product-list--list-item'})
            except:
                break
            # print("PAGE", params['page'])
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


            # print("PRODUCTS:", no_prod)
            # print('----------')
            if no_prod or retries == 100:
                params['page'] += 1
                retries = 0
            else:
                retries += 1

