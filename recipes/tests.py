from django.test import TestCase

from users.models import Account
from .models import Recipe

# Create your tests here.
class TestUserForms(TestCase):
    ## ----------- TEST MODELS --------------
    def test_successfully_create_recipe_with_valid_data(self):
        tesco =  [1, 2, 3]
        british_on = [2, 3, 4]
        # create user
        user = Account.objects.create(username='testUSER', email='test2@test.com', is_email_verified=True)
        recipe = Recipe.objects.create(
                user=user,
                products_tesco=tesco,
                products_british_online_supermarket=british_on,
        )
        retrieved_recipe = Recipe.objects.get(pk=recipe.pk)
        self.assertEqual(retrieved_recipe.user, user)
        self.assertEqual(retrieved_recipe.products_tesco, tesco)
        self.assertEqual(retrieved_recipe.products_british_online_supermarket, british_on)

    def test_save_recipe_invalid_user_not_allowed(self):
        tesco =  [1, 2, 3]
        british_on = [2, 3, 4]
        try:
            recipe = Recipe.objects.create(
                    user='usertest',
                    products_tesco=tesco,
                    products_british_online_supermarket=british_on,
            )
            self.fail()
        except:
            pass
    
    def test_save_recipe_no_user_not_allowed(self):
        tesco =  [1, 2, 3]
        british_on = [2, 3, 4]
        try:
            recipe = Recipe.objects.create(
                    products_tesco=tesco,
                    products_british_online_supermarket=british_on,
            )
            self.fail()
        except:
            pass
    
    def test_save_recipe_invaliv_products_tesco_not_allowed(self):
        british_on = [2, 3, 4]
        user = Account.objects.create(username='testUSER', email='test2@test.com', is_email_verified=True)
        try:
            recipe = Recipe.objects.create(
                    user=user,
                    products_tesco='das',
                    products_british_online_supermarket=british_on,
            )
            self.fail()
        except:
            pass

    def test_save_recipe_no_products_tesco_not_allowed(self):
        british_on = [2, 3, 4]
        user = Account.objects.create(username='testUSER', email='test2@test.com', is_email_verified=True)
        try:
            recipe = Recipe.objects.create(
                    user=user,
                    products_british_online_supermarket=british_on,
            )
            self.fail()
        except:
            pass
    
    def test_save_recipe_no_products_british_online_supermarket_not_allowed(self):
        tesco = [2, 3, 4]
        user = Account.objects.create(username='testUSER', email='test2@test.com', is_email_verified=True)
        try:
            recipe = Recipe.objects.create(
                    user=user,
                    products_tesco=tesco,
            )
            self.fail()
        except:
            pass

    def test_save_recipe_invalid_products_british_online_supermarket_not_allowed(self):
        tesco = [2, 3, 4]
        user = Account.objects.create(username='testUSER', email='test2@test.com', is_email_verified=True)
        try:
            recipe = Recipe.objects.create(
                    user=user,
                    products_tesco=tesco,
                    products_british_online_supermarket='random',
            )
            self.fail()
        except:
            pass

