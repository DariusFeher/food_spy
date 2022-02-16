from bs4 import BeautifulSoup
import requests, lxml
import time
import csv
import re
from background_task import background
from supermarkets_data.models import SainsburysData
from tesco_products.utils import clean_mention
import cloudscraper
from .models import SainsburysProduct

import nltk

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
        'Referer': 'http://www.sainsburys.co.uk/'
        }

BASE_URL = 'https://www.sainsburys.co.uk/'

category_urls = {
	'fruits-and-vegetables' : 'https://www.sainsburys.co.uk/shop/CategorySeeAllView?pageSize=60&orderBy=FAVOURITES_FIRST&storeId=10151&categoryFacetId1=12518&promotionId=&listId=&catalogId=10241&searchTerm=&beginIndex=0&top_category=&langId=44&categoryId=12518&parent_category_rn=#langId=44&storeId=10151&catalogId=10241&categoryId=12518&parent_category_rn=&top_category=&pageSize=60&orderBy=FAVOURITES_FIRST&searchTerm=&catSeeAll=true&beginIndex=0&categoryFacetId1=12518&categoryFacetId2=',
	'meat-and-fish' : 'https://www.sainsburys.co.uk/shop/CategorySeeAllView?listId=&catalogId=10241&searchTerm=&beginIndex=0&pageSize=60&orderBy=FAVOURITES_FIRST&top_category=&langId=44&storeId=10151&categoryId=13343&promotionId=&parent_category_rn=#langId=44&storeId=10151&catalogId=10241&categoryId=13343&parent_category_rn=&top_category=&pageSize=60&orderBy=FAVOURITES_FIRST&searchTerm=&catSeeAll=true&beginIndex=0&categoryFacetId1=13343&categoryFacetId2=',
	'dairy-and-chilled' : 'https://www.sainsburys.co.uk/shop/CategorySeeAllView?listId=&catalogId=10241&searchTerm=&beginIndex=0&pageSize=60&orderBy=FAVOURITES_FIRST&top_category=&langId=44&storeId=10151&categoryId=428866&promotionId=&parent_category_rn=', 
	'bakery' : 'https://www.sainsburys.co.uk/shop/CategorySeeAllView?listId=&catalogId=10241&searchTerm=&beginIndex=0&pageSize=60&orderBy=FAVOURITES_FIRST&top_category=&langId=44&storeId=10151&categoryId=12320&promotionId=&parent_category_rn=',
	'frozen' : 'https://www.sainsburys.co.uk/shop/CategorySeeAllView?listId=&catalogId=10241&searchTerm=&beginIndex=0&pageSize=60&orderBy=FAVOURITES_FIRST&top_category=&langId=44&storeId=10151&categoryId=218831&promotionId=&parent_category_rn=',
	'food-cupboard' : 'https://www.sainsburys.co.uk/shop/CategorySeeAllView?listId=&catalogId=10241&searchTerm=&beginIndex=0&pageSize=60&orderBy=FAVOURITES_FIRST&top_category=&langId=44&storeId=10151&categoryId=12192&promotionId=&parent_category_rn=',
}

params = {
	'page' : 1,
}

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('wordnet')

def get_price_and_currency(price_and_currency_string):
	if price_and_currency_string.endswith('p'):
		price = price_and_currency_string[:-1]
		currency = '£'
		price = int(price) / 100.0
		return (price, currency)
	else:
		currency = price_and_currency_string[0]
		price = price_and_currency_string[1:]
		return (price, currency)


@background
def update_sainsburys_products_db():
    print("INSIDE...")
    entities = {}
    protected_tokens = set()
    entities_with_ids = {}
    ids = set()
    for category in category_urls:
        retries = 0
        params['page'] = 1
        print("PAGE", params['page'])
        current_url = category_urls[category]
        while True:
            scraper = cloudscraper.create_scraper()
            html = scraper.get(current_url, headers=headers).text
            time.sleep(0.5)
            soup = BeautifulSoup(html, 'html.parser')
            try:
                prodList = soup.findAll('li', {'class' : 'gridItem'})
            except:
                break
            no_prod = 0
            if not prodList:
                retries = 0
                print("No products on this page")
                break
            for product in prodList:
                try:
                    link = product.find('div', {'class' : "productNameAndPromotions"}).find('a')['href']
                    title = product.find('div', {'class' : "productNameAndPromotions"}).find('a').text.strip()
                    product_id = product.find('input', {'name' : "productId"})['value']
                    price, currency = get_price_and_currency(product.find('p', {'class' : 'pricePerUnit'}).text.strip())
                    no_prod += 1
                    if no_prod == 1:
                        print(title)
                except:
                    print('Error')
                    continue
                try:
                    product = SainsburysProduct.objects.get(id=id_product) 
                except:
                    product = None
                if product:
                    product.price = price
                    product.currency = currencies[currency]
                    product.link = link
                    product.full_name = title
                    product.save()
                else:
                    product = SainsburysProduct(
                        price = price,
                        currency = currencies[currency],
                        link = link,
                        full_name = title,
                        id = product_id
                    )
                    product.save()

                no_prod += 1
                ids.add(product_id)
                cleaned_entity= clean_mention(title)

                new_prod = {}
                new_prod['price'] = price
                new_prod['currency'] = currency
                new_prod['full_name'] = title
                new_prod['link'] = link
                new_prod['cleaned_full_name'] = cleaned_entity
                new_prod['id'] = product_id
                entities[product_id] = new_prod

                if cleaned_entity not in entities_with_ids:
                    entities_with_ids[cleaned_entity] = []
                entities_with_ids[cleaned_entity].append(new_prod['id'])

                text = nltk.word_tokenize(new_prod['cleaned_full_name'])
                tags = nltk.pos_tag(text, tagset='universal')
                
                for tag in tags:
                    if tag[1] == 'NOUN':
                        protected_tokens.add(tag[0])
            
            if no_prod or retries == 100:
                print("PRODUCTS:", no_prod)
                print('----------')

                # print(soup.prettify())
                param = 'beginIndex=' + str(60 * (params['page'] - 1))
                nextPage = 'beginIndex=' + str(60 * (params['page']))
                current_url = current_url.replace(param, nextPage)
                params['page'] += 1

                print("PAGE", params['page'])
                retries = 0
            else:
                retries += 1
                print("RETRYING")

    # Delete last lists of entities and protected tokens            
    sainsburysDataObj = SainsburysData.objects.all()
    if len(sainsburysDataObj) > 0:
        sainsburysDataObj = sainsburysDataObj[0]
        sainsburysDataObj.delete()

    # Replace them with the updated ones
    sainsburysDataObj = SainsburysData(
        products_data = entities,
        protected_tokens = list(protected_tokens),
        products_entities = entities_with_ids,
    )
    sainsburysDataObj.save()

    # Delete the products which are not part of Amazon's offer
    sainsburysProducts = SainsburysProduct.objects.all()
    for product in sainsburysProducts: 
        if product.id not in ids:
            product.delete()