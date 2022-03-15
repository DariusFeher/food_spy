from django.test import TestCase

from users.models import Account
from recipes.models import Recipe

# Create your tests here.
class TestUserForms(TestCase):
    def test_homepage_view__exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_view_renders_correct_template(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_homepage_view_post_request(self):
        response = self.client.post('/', {'recipe_link': 'https://www.bbcgoodfood.com/recipes/chicken-chorizo-ragu'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_homepage_accessible_if_logged_in(self):
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()
        data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
        self.client.post('/login/', data)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_get_recipe_ingredients_prices_returns_success(self):
        response = self.client.get('/get_prices/')
        self.assertEqual(response.status_code, 200)
    
    def test_post_to_get_recipe_ingredients_prices_returns_success(self):
        response = self.client.post('/get_prices/', {'ingredient_nr': [1], 'ingredient_name': 'tomato'})
        self.assertEqual(response.status_code, 200)
    
    def test_save_recipe_not_allowed_if_not_logged_in(self):
        response = self.client.get('/myrecipes/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/myrecipes/')


    def test_save_recipe_get_allowed_if_logged_in(self):
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()
        data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
        self.client.post('/login/', data)

        response = self.client.get('/myrecipes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_recipes.html')
    
    def test_save_recipe_post_allowed_if_logged_in(self):
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()
        data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
        self.client.post('/login/', data)

        session = self.client.session
        self.product = {
                        'tomato':
                                [
                                    {
                                        "cleaned_full_name": "salad tomato", 
                                        "cleaned_short_name": "tomato", 
                                        "currency": "\u00a3", 
                                        "full_name": "Tesco Salad Tomatoes", 
                                        "id": "304401366", 
                                        "link": "https://www.tesco.com/groceries/en-GB/products/304401366", 
                                        "price": "0.14", 
                                        "short_name": "Tomatoes"
                                    }
                                ]       
                        }
        session['tesco_products'] = self.product
        session['british_online_supermarket_products'] = self.product
        session.save()
        response = self.client.post('/myrecipes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_recipes.html')

    def test_get_recipe_price_comparison_not_allowed_if_not_logged_in(self):
            response = self.client.get('/myrecipes/1/price_compare')
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '/login/?next=/myrecipes/1/price_compare')

    def test_get_recipe_price_comparison_post_not_allowed_if_not_logged_in(self):
            response = self.client.post('/myrecipes/1/price_compare')
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '/login/?next=/myrecipes/1/price_compare')

    def test_get_recipe_price_comparison_allowed_if_logged_in(self):
            data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
            self.client.post('/register/', data)
            account = Account.objects.get(username='testUserPostVerified')
            account.is_email_verified = True
            account.save()
            data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
            self.client.post('/login/', data)

            session = self.client.session
            self.product = {
                            'tomato':
                                    [
                                        {
                                            "cleaned_full_name": "salad tomato", 
                                            "cleaned_short_name": "tomato", 
                                            "currency": "\u00a3", 
                                            "full_name": "Tesco Salad Tomatoes", 
                                            "id": "304401366", 
                                            "link": "https://www.tesco.com/groceries/en-GB/products/304401366", 
                                            "price": "0.14", 
                                            "short_name": "Tomatoes"
                                        }
                                    ]       
                            }
            session['tesco_products'] = self.product
            session['british_online_supermarket_products'] = self.product
            session.save()
            response = self.client.post('/myrecipes/')
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'my_recipes.html')
            recipe = Recipe.objects.get(user=account)
            print(recipe.pk)
            url = '/myrecipes/'+ str(recipe.pk) + '/price_compare'
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'recipe_prices_comparison.html')

    def test_get_recipe_price_comparison_post_allowed_if_logged_in(self):
            data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
            self.client.post('/register/', data)
            account = Account.objects.get(username='testUserPostVerified')
            account.is_email_verified = True
            account.save()
            data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
            self.client.post('/login/', data)

            session = self.client.session
            self.product = {
                            'tomato':
                                    [
                                        {
                                            "cleaned_full_name": "salad tomato", 
                                            "cleaned_short_name": "tomato", 
                                            "currency": "\u00a3", 
                                            "full_name": "Tesco Salad Tomatoes", 
                                            "id": "304401366", 
                                            "link": "https://www.tesco.com/groceries/en-GB/products/304401366", 
                                            "price": "0.14", 
                                            "short_name": "Tomatoes"
                                        }
                                    ]       
                            }
            session['tesco_products'] = self.product
            session['british_online_supermarket_products'] = self.product
            session.save()
            response = self.client.post('/myrecipes/')
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'my_recipes.html')
            recipe = Recipe.objects.get(user=account)
            print(recipe.pk)
            url = '/myrecipes/'+ str(recipe.pk) + '/price_compare'
            response = self.client.post(url, {'ingredient_nr': [1], 'ingredient_name': 'tomato'})
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'recipe_prices_comparison.html')

    def test_delete_recipe_not_allowed_if_not_logged_in(self):
        # Save recipe
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()
        data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
        self.client.post('/login/', data)

        session = self.client.session
        self.product = {
                                        'tomato':
                                                [
                                                    {
                                                        "cleaned_full_name": "salad tomato", 
                                                        "cleaned_short_name": "tomato", 
                                                        "currency": "\u00a3", 
                                                        "full_name": "Tesco Salad Tomatoes", 
                                                        "id": "304401366", 
                                                        "link": "https://www.tesco.com/groceries/en-GB/products/304401366", 
                                                        "price": "0.14", 
                                                        "short_name": "Tomatoes"
                                                    }
                                                ]       
                                        }
        session['tesco_products'] = self.product
        session['british_online_supermarket_products'] = self.product
        session.save()
        response = self.client.post('/myrecipes/')
        self.client.get('/logout/')
        response = self.client.get('/myrecipes/1/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/myrecipes/1/delete/')
    
    def test_delete_recipe_allowed_if_logged_in(self):
        # Save recipe
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()
        data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
        self.client.post('/login/', data)

        session = self.client.session
        self.product = {
                        'tomato':
                                [
                                    {
                                        "cleaned_full_name": "salad tomato", 
                                        "cleaned_short_name": "tomato", 
                                        "currency": "\u00a3", 
                                        "full_name": "Tesco Salad Tomatoes", 
                                        "id": "304401366", 
                                        "link": "https://www.tesco.com/groceries/en-GB/products/304401366", 
                                        "price": "0.14", 
                                        "short_name": "Tomatoes"
                                    }
                                ]       
                        }
        session['tesco_products'] = self.product
        session['british_online_supermarket_products'] = self.product
        session.save()
        response = self.client.post('/myrecipes/')
        response = self.client.get('/myrecipes/1/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/myrecipes/')




