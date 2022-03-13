from django.test import TestCase

from .models import BritishOnlineSupermarketProduct

# Create your tests here.
class TestUserForms(TestCase):
    ## ----------- TEST MODELS --------------
    def test_success_save_with_valid_data(self):
        britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                id='10',
                price=1.05,
                currency='2',
                full_name='placeholder_fn',
                link='placeholder_link'
        )
        product = BritishOnlineSupermarketProduct.objects.get(id='10')
        self.assertEqual(product.full_name, 'placeholder_fn')
        self.assertEqual(product.price, 1.05)
        self.assertEqual(product.currency, '2')
        self.assertEqual(product.link, 'placeholder_link')
    
    def test_empty_id_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    price='312',
                    currency='2',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass
    
    def test_long_id_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1' * 31,
                    price=1.05,
                    currency='2',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass
    
    def test_empty_price_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    currency='2',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass

    def test_price_int_is_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    price=10,
                    currency='2',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass

    def test_price_not_float_or_int_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    price='312',
                    currency='2',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass
    
    def test_empty_currency_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    price='312',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass

    def test_currency_1_2_3_is_allowed(self):
        britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                id='1',
                price=1,
                currency='1',
                full_name='placeholder_fn',
                link='placeholder_link'
        )
        product = BritishOnlineSupermarketProduct.objects.get(id='1')
        self.assertEqual(product.currency, '1')

        britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                id='2',
                price=1,
                currency='2',
                full_name='placeholder_fn',
                link='placeholder_link'
        )

        product = BritishOnlineSupermarketProduct.objects.get(id='2')
        self.assertEqual(product.currency, '2')

        britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                id='3',
                price=1,
                currency='3',
                full_name='placeholder_fn',
                link='placeholder_link'
        )
        product = BritishOnlineSupermarketProduct.objects.get(id='3')
        self.assertEqual(product.currency, '3')
    
    def test_currency_other_than_1_2_3_is_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    price=1,
                    currency='5',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail()
        except:
            pass
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='2',
                    price=1,
                    currency='0',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail()
        except:
            pass
        
        try:
            product = BritishOnlineSupermarketProduct.objects.get(id='2')
            self.assertEqual(product.currency, '2')

            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='3',
                    price=1,
                    currency='102',
                    full_name='placeholder_fn',
                    link='placeholder_link'
            )
            self.fail()
        except:
            pass
    
    
    
    def test_empty_long_name_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    price='312',
                    currency='2',
                    link='placeholder_link'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass
    
    def test_too_long_long_name_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    price=1.05,
                    currency='2',
                    full_name='t' * 301,
                    link='placeholder_link'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass
    
    def test_empty_link_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    price='312',
                    currency='2',
                    full_name='placeholder_fn'
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass

    def test_too_long_link_name_not_allowed(self):
        try:
            britishOnlineSupermarketProduct = BritishOnlineSupermarketProduct.objects.create(
                    id='1',
                    price=1.05,
                    currency='2',
                    full_name='placeholder_fn',
                    link='l' * 2001
            )
            self.fail() # If it gets here, then it has been saved
        except:
            pass
    
    ## -------- END TEST MODELS --------
    