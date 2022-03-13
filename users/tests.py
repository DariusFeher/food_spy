from django.test import TestCase

from .forms import CreateUserForm
from .models import Account

# Create your tests here.
class TestUserForms(TestCase):
    ## ----------- TEST MODELS AND FORMS --------------
    def test_valid_login_form(self):
        data = {'username': 'testUSER', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        form = CreateUserForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_username_too_long_not_allowed(self):
        data = {'username': 't' * 31, 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        form = CreateUserForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_email_too_long_not_allowed(self):
        email = 'test@test.com' + 't' * 50
        data = {'username': 'testUser', 'email': email, 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        form = CreateUserForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_invalid_email_not_allowed(self):
        data = {'username': 'testUser', 'email': 'test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        form = CreateUserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_empty_email_not_allowed(self):
        data = {'username': 'testUser', 'email': '', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        form = CreateUserForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_empty_username_not_allowed(self):
        data = {'username': '', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        form = CreateUserForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_empty_password_not_allowed(self):
        data = {'username': 'testUser', 'email': 'test@test.com', 'password1': '!S!Ss', 'password2': 'password1234£!S!Ss'}
        form = CreateUserForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_different_passwords_not_allowed(self):
        data = {'username': 'test', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': '234£!S!Sspassword1'}
        form = CreateUserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_create_account_with_same_email_not_allowed(self):
        account = Account.objects.create(username='testUSER', email='test2@test.com', is_email_verified=True)
        try:
            account2 = Account.objects.create(username='testUSER2', email='test2@test.com', is_email_verified=True)
            self.fail()
        except:
            pass

    def test_create_account_with_same_user_not_allowed(self):
        account = Account.objects.create(username='testUSER', email='test@test.com', is_email_verified=True)
        try:
            account2 = Account.objects.create(username='testUSER', email='test2@test.com', is_email_verified=True)
            self.fail()
        except:
            pass

    def test_create_account_with_same_user_same_email_not_allowed(self):
        account = Account.objects.create(username='testUSER', email='test@test.com', is_email_verified=True)
        try:
            account2 = Account.objects.create(username='testUSER', email='test@test.com', is_email_verified=True)
            self.fail()
        except:
            pass

    ## ----------- END OF TESTING MODELS ----------------

    ## ---------------- TESTING VIEWS -------------------

    # REGISTER VIEW
    def test_register_view_exists_at_desired_location(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_register_view_renders_correct_template(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_register_view_post_data_successfully_redirects_to_login(self):
        data = {'username': 'testUserPost', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        response = self.client.post('/register/', data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')
        account = Account.objects.get(username='testUserPost')
        self.assertIsNotNone(account)
    
    def test_register_view_post_data_invalid_form_renders_register(self):
        # INVALID EMAIL => INVALID FORM
        data = {'username': 'testUserPost', 'email': 'testtest.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        response = self.client.post('/register/', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    # LOGIN VIEW
    def test_login_view_exists_at_desired_location(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_view_renders_correct_template(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_login_view_unsuccessful_with_unverified_email(self):
        # Firstly register user
        data = {'username': 'testUserPost', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        data = {'username': 'testUserPost', 'password1': 'password1234£!S!Ss'}
        response = self.client.post('/login/', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_login_view_successful_with_verified_email(self):
        # Firstly register user
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()
        data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
        response = self.client.post('/login/', data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
    
    def test_login_view_fails_with_invalid_credentials(self):
        # INVALID EMAIL => INVALID FORM
        data = {'username': 'RANDOMUSER', 'password1': 'RANDOMPASSWORD'}
        response = self.client.post('/login/', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    # LOGOUT VIEW
    def test_logout(self):
        # Register and Login user
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()
        data = {'username': 'testUserPostVerified', 'password1': 'password1234£!S!Ss'}
        self.client.post('/login/', data)
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')

    # GET NEW ACTIVATION LINK VIEW
    def test_new_activation_link_view_exists_at_desired_location(self):
        response = self.client.get('/resend-link/')
        self.assertEqual(response.status_code, 200)

    def test_new_activation_link_view_renders_correct_template(self):
        response = self.client.get('/resend-link/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/resend_activation.html')
    
    def test_new_activation_link_view_post_redirects_to_login(self):
        # Register user
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()

        response = self.client.post('/resend-link/', {'email': 'test@test.com'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')

    # Request reset password
    def test_request_reset_password_view_exists_at_desired_location(self):
        response = self.client.get('/request-reset-password/')
        self.assertEqual(response.status_code, 200)

    def test_request_reset_password_view_renders_correct_template(self):
        response = self.client.get('/request-reset-password/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/reset_password_request.html')
    
    def test_request_reset_password_view_post_redirects_to_login(self):
        # Register user
        data = {'username': 'testUserPostVerified', 'email': 'test@test.com', 'password1': 'password1234£!S!Ss', 'password2': 'password1234£!S!Ss'}
        self.client.post('/register/', data)
        account = Account.objects.get(username='testUserPostVerified')
        account.is_email_verified = True
        account.save()

        response = self.client.post('/request-reset-password/', {'email': 'test@test.com'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    # Activate user
    def test_activate_user_redirects_to_login(self):
        response = self.client.post('/activate-user/MTA/aqiddg-8c805fd88fc489968b5b142ee1bf9373')
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, '/login/')
    
    # Resend activation link
    def test_activation_link_renders_right_template(self):
        response = self.client.get('/resend-link/')
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'accounts/resend_activation.html')
    
    def test_successfull_activation_link_redirects_to_login(self):
        response = self.client.post('/resend-link/', {'email': 'test@test.com'})
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, '/login/')
    
    def test_reset_password_view_renders_right_template(self):
        response = self.client.get('/reset-password/MTA/aqiddg-8c805fd88fc489968b5b142ee1bf9373')
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'accounts/reset_password_confirm.html')

    ## ---------------- END OF TESTING VIEWS -------------------