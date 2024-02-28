from django.test import TestCase, Client, RequestFactory
from django.urls import resolve, reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.contrib.auth.models import User

from registration.views import check_data, registration, activate_account
from registration.forms import RegistrationForm
from registration import views


class TestRegistrationForms(TestCase):
    def test_registration_form_save(self):
        registration_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }

        form = RegistrationForm(data=registration_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.username, registration_data['username'])
        self.assertEqual(user.first_name, registration_data['first_name'].lower())
        self.assertEqual(user.last_name, registration_data['last_name'].lower())
        self.assertEqual(user.email, registration_data['email'])
        self.assertTrue(user.check_password(registration_data['password1']))


class TestRegistrationUrls(TestCase):
    def test_home_url_resolves(self):
        resolved_view = resolve('/registration/')
        self.assertEqual(resolved_view.func, views.registration)
        self.assertEqual(resolved_view.url_name, 'registration')


class TestRegistrationViews(TestCase):
    def setUp(self):
        User.objects.create(username='existinguser', email='existinguser@example.com')
        self.client = Client()

    def test_check_data_passwords_not_same(self):
        error_message = check_data('newuser', 'newuser@example.com')
        self.assertEqual(error_message, 'This password is too short. '
                                        'It must contain at least 8 characters., '
                                        'This password is too common.')

    def test_registration_view_post(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'test',
            'last_name': 'user',
            'password1': 'Testpassword_123',
            'password2': 'Testpassword_123',
        }

        response = self.client.post('/registration/', data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/welcome.html')

        self.assertIn('username', response.context)
        self.assertIn('email', response.context)

        self.assertEqual(response.context['username'], 'testuser')
        self.assertEqual(response.context['email'], 'test@example.com')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Confirm your registration', mail.outbox[0].subject)
        self.assertIn('Please confirm your email address to get full access to DjangoGram', mail.outbox[0].body)

        self.assertTemplateUsed(response, 'registration/welcome.html')
        self.assertTrue(User.objects.filter(username='testuser').exists())

        testuser = User.objects.get(username='testuser')
        self.assertFalse(testuser.is_active)

    def test_registration_error_page(self):
        data = {
            'username': 'existing_user',
            'email': 'existing_user@example.com',
            'password1': 'short',
            'password2': 'short',
        }

        response = self.client.post(reverse('registration'), data, follow=True)

        self.assertTemplateUsed(response, 'registration/error_registration.html')

    def test_registration_view_get(self):
        response = self.client.get('/registration/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration.html')

        self.assertIn('form', response.context)


class TestRegistrationViewsActivateAccount(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.activation_code = 1234

    def test_activate_account_correct_code(self):
        request = self.factory.post('/activate_account/', {'user_entered_code': self.activation_code})

        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)

        request.session['activation_code'] = self.activation_code
        request.session['username'] = 'testuser'
        response = activate_account(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        activated_user = User.objects.get(username='testuser')
        self.assertTrue(activated_user.is_active)
        self.assertEqual(str(activated_user), 'testuser')

    def test_activate_account_incorrect_code(self):
        request = self.factory.post('/activate_account/', {'user_entered_code': 5678})

        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)

        request.session['activation_code'] = self.activation_code
        request.session['username'] = 'testuser'
        response = activate_account(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid activation code. Please try again.', response.content.decode())
