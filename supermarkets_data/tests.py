from django.test import TestCase

from .models import TescoData, BritishOnlineSupermarketData

# Create your tests here.
class TestUserForms(TestCase):
    ## ----------- TEST MODELS --------------
    # TESCO DATA TESTS
    def test_success_save_tesco_data_with_valid_data(self):
        tokens = [1, 2, 3]
        products = [0, 5, 15]
        tesco_data = TescoData.objects.create(
                protected_tokens = tokens,
                products_data = products
        )
        retrieved_tesco_data = TescoData.objects.get(pk=tesco_data.pk)
        self.assertEqual(retrieved_tesco_data.protected_tokens, tokens)
        self.assertEqual(retrieved_tesco_data.products_data, products)
    
    def test_save_tesco_data_with_invalid_data_not_allowed(self):
        try:
            tesco_data = TescoData.objects.create(
                    protected_tokens = 'random_token',
                    products_data = 'random_data'
            )
            self.fail()
        except:
            pass
    
    def test_save_tesco_data_with_empty_data_not_allowed(self):
        try:
            tesco_data = TescoData.objects.create(
            )
            self.fail()
        except:
            pass
    
    def test_save_tesco_data_with_empty_tokens_not_allowed(self):
        try:
            products = [0, 5, 15]
            tesco_data = TescoData.objects.create(
                    products_data = products
            )
            self.fail()
        except:
            pass
    
    def test_save_tesco_data_with_empty_products_not_allowed(self):
        try:
            tokens = [1, 2, 3]
            tesco_data = TescoData.objects.create(
                    protected_tokens = tokens,
            )
            self.fail()
        except:
            pass
    
    # BRITISH ONLINE SUPERMARKET DATA TESTS

    def test_success_save_british_online_supermarket_data_with_valid_data(self):
        tokens = [1, 2, 3]
        products = [0, 5, 15]
        entities = [15, 12, 12]
        british_data = BritishOnlineSupermarketData.objects.create(
                protected_tokens = tokens,
                products_data = products,
                products_entities = entities,
        )
        retrieved_british_data = BritishOnlineSupermarketData.objects.get(pk=british_data.pk)
        self.assertEqual(retrieved_british_data.protected_tokens, tokens)
        self.assertEqual(retrieved_british_data.products_data, products)
        self.assertEqual(retrieved_british_data.products_entities, entities)

    
    def test_save_british_online_supermarket_data_with_invalid_data_not_allowed(self):
        try:
            british_data = BritishOnlineSupermarketData.objects.create(
                    protected_tokens = 'random_token',
                    products_data = 'random_data',
                    entities = 'random_entity'
            )
            self.fail()
        except:
            pass
    
    def test_save_british_online_supermarket_data_with_empty_data_not_allowed(self):
        try:
            british_data = BritishOnlineSupermarketData.objects.create(
            )
            self.fail()
        except:
            pass
    
    def test_save_british_online_supermarket_data_with_empty_tokens_not_allowed(self):
        try:
            products = [0, 5, 15]
            entities = [15, 12, 12]
            british_data = BritishOnlineSupermarketData.objects.create(
                    products_data = products,
                    products_entities = entities,
            )
            self.fail()
        except:
            pass
    
    def test_save_british_online_supermarket_data_with_empty_products_data_not_allowed(self):
        try:
            tokens = [1, 2, 3]
            entities = [15, 12, 12]
            british_data = BritishOnlineSupermarketData.objects.create(
                    protected_tokens = tokens,
                    products_entities = entities,
            )
            self.fail()
        except:
            pass
    
    def test_save_british_online_supermarket_data_with_empty_products_entities_not_allowed(self):
        try:
            tokens = [1, 2, 3]
            products = [0, 5, 15]
            british_data = BritishOnlineSupermarketData.objects.create(
                    protected_tokens = tokens,
                    products_data = products,
            )
            self.fail()
        except:
            pass

