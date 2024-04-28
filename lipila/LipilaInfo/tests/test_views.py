from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest import mock
# Custom modules
from business.models import BusinessUser
from patron.models import CreatorUser
from LipilaInfo.models import LipilaUser, Patron, ContactInfo, LipilaHome, Testimonial
from LipilaInfo.helpers import get_user_object, check_if_user_is_patron
from LipilaInfo.forms.forms import ContactForm


class IndexViewTest(TestCase):
    def setUp(self):
        # Create test data (consider using @skip_unless for helper functions)
        ContactInfo.objects.create(
            street="Test Street",
            location="Test Location",
            phone1="123-456-7890",
            email1="test@example.com",
        )
        LipilaHome.objects.create(
            message="Test message",
            slogan="Test slogan",
        )
        Testimonial.objects.create(user=LipilaUser.objects.create(username="test_user"), message="Test testimonial")

    def test_index_view_success(self):
        """Test index view renders successfully with context data"""
        url = reverse('index')  # Generate the URL for the index view
        response = self.client.get(url)

        # Assert HTTP status code
        self.assertEqual(response.status_code, 200)

        # Assert template used
        self.assertTemplateUsed(response, 'UI/index.html')

        # Assert context data (consider using more specific assertions)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ContactForm)
        self.assertIn('contact', response.context)
        self.assertIn('lipila', response.context)
        self.assertIn('testimony', response.context)

class TestJoinView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_object = LipilaUser.objects.create_user(
            'test_user', 'test@example.com', 'password123')
        self.creator_object = CreatorUser.objects.create_user(
            'creator_user', 'creator@example.com', 'password123')

    def test_get_not_logged_in(self):
        """Test GET request without login"""
        response = self.client.get(reverse(
            'join', kwargs={'user': self.user_object, 'creator': self.creator_object}))
        # Redirect to login page (302)
        self.assertEqual(response.status_code, 302)

    def test_get_logged_in_not_patron(self):
        """Test GET request, logged in but not a patron"""
        self.client.login(username='test_user', password='password123')
        response = self.client.get(reverse(
            'join', kwargs={'user': self.user_object, 'creator': self.creator_object}))
        # Successful GET request (200)
        self.assertEqual(response.status_code, 200)
        # Check for used template
        self.assertTemplateUsed(response, 'LipilaInfo/admin/join.html')

    def test_get_logged_in_patron_not_subscribed(self):
        """Test GET request, logged in as patron but not subscribed"""
        Patron.objects.create(user=self.user_object)
        self.client.login(username='test_user', password='password123')
        response = self.client.get(reverse(
            'join', kwargs={'user': self.user_object, 'creator': self.creator_object}))
        # Successful GET request (200)
        self.assertEqual(response.status_code, 200)
        # Check for used template
        self.assertTemplateUsed(response, 'LipilaInfo/admin/join.html')
        # Check if 'is_patron' is False
        self.assertFalse(response.context['is_patron'])

    def test_get_logged_in_patron_subscribed(self):
        """Test GET request, logged in as patron and already subscribed"""
        patron = Patron.objects.create(user=self.user_object)
        patron.patron.add(self.creator_object)
        self.client.login(username='test_user', password='password123')
        response = self.client.get(reverse(
            'join', kwargs={'user': self.user_object, 'creator': self.creator_object}))
        # Successful GET request (200)
        self.assertEqual(response.status_code, 200)
        # Check for used template
        self.assertTemplateUsed(response, 'LipilaInfo/admin/join.html')
        # Check if 'is_patron' is True
        self.assertTrue(response.context['is_patron'])

    def test_post_not_logged_in(self):
        """Test POST request without login"""
        response = self.client.post(reverse(
            'join', kwargs={'user': self.user_object, 'creator': self.creator_object}))
        # Redirect to login page (302)
        self.assertEqual(response.status_code, 302)

    def test_post_invalid_form(self):
        """Test POST request with invalid form"""
        self.client.login(username='test_user', password='password123')
        response = self.client.post(reverse('join', kwargs={
                                    'user': self.user_object, 'creator': self.creator_object}), {'invalid_field': 'invalid_data'})
        self.assertEqual(response.status_code, 200)  # Render form again (200)
        # Check for used template
        self.assertTemplateUsed(response, 'LipilaInfo/admin/join.html')

    # Mock the check_if_user_is_patron function
    @mock.patch('LipilaInfo.helpers.check_if_user_is_patron')
    def test_post_valid_form_new_patron(self, mock_check):
        """Test POST request with valid form, creating a new Patron"""

        # Mock the check_if_user_is_patron function to return False (user is not a patron)
        mock_check.return_value = False

        self.client.login(username='test_user', password='password123')
        data = {'subscription': 'one'}  # Replace with actual form field names
        response = self.client.post(reverse(
            'join', kwargs={'user': self.user_object, 'creator': self.creator_object}), data)

        # Check for successful form submission and redirection
        self.assertEqual(response.status_code, 302)
        # Redirect to patron list after successful join
        self.assertEqual(response.url, reverse('patron'))
        self.assertTemplateUsed('LipilaInfo/admin/patron.html')
        # Assert that Patron object is created and saved
        patron = Patron.objects.get(user=self.user_object)
        # Check if Patron has a primary key (saved)
        self.assertTrue(patron.pk is not None)

        # # Assert that the creator is added to the patron's patron
        # self.assertTrue(patron.patron.filter(pk=self.creator_object.pk).exists())

        # # Verify that check_if_user_is_patron was called with expected arguments
        # mock_check.assert_called_once_with(self.user_object, self.creator_object)


class TestCheckIfUserIsPatron(TestCase):
    def setUp(self):
        # Create a LipilaUser (or User) for testing
        self.user_object = LipilaUser.objects.create_user(
            'test_user', 'test@example.com', 'password123')
        self.creator_object = CreatorUser.objects.create_user(
            'test_creator', 'test1@example.com', 'password123')

    def test_user_is_patron_false(self):
        # Create a Patron object for the user
        Patron.objects.create(user=self.user_object)

        is_patron = check_if_user_is_patron(
            self.user_object, self.creator_object)
        self.assertFalse(is_patron)

    def test_user_is_not_patron_no_patron_object(self):
        # User exists but doesn't have a Patron
        is_patron = check_if_user_is_patron(
            self.user_object, self.creator_object)
        self.assertFalse(is_patron)


class GetUserObjectTest(TestCase):
    def setUp(self):
        # Create test users of each type (replace with your data)
        self.business_user = BusinessUser.objects.create_user(
            username='business_user', password='business_password', is_active=True)
        self.patron_user = CreatorUser.objects.create_user(
            username='patron_user', password='patron_password', is_active=True)
        self.lipila_user = LipilaUser.objects.create_user(
            username='lipila_user', password='lipila_password', is_active=True)

    def test_get_business_user_object(self):
        """Test the successful gettting of a BusinessUser and return Object"""
        user_object = get_user_object(self.business_user)
        self.assertTrue(type(user_object), BusinessUser)
        self.assertEqual(type(user_object), BusinessUser)

    def test_get_patron_user_object(self):
        """Test the successful gettting of a CreatorUser and return Object"""
        user_object = get_user_object(self.patron_user)
        self.assertTrue(type(user_object), CreatorUser)

    def test_get_lipila_user_object(self):
        """Test the successful gettting of a LipilaUser and return Object"""
        user_object = get_user_object(self.lipila_user)
        self.assertTrue(type(user_object), LipilaUser)

    def test_get_business_user_object_failure(self):
        """Test the failure gettting of a Business User and return Object"""
        user_object = get_user_object('test_user')
        self.assertEqual(user_object['status'], 404)


class LoginViewTest(TestCase):

    def setUp(self):
        # Create test users of each type (replace with your data)
        self.business_user = BusinessUser.objects.create_user(
            username='business_user', password='business_password', is_active=True)
        self.patron_user = CreatorUser.objects.create_user(
            username='patron_user', password='patron_password', is_active=True)
        self.lipila_user = LipilaUser.objects.create_user(
            username='lipila_user', password='lipila_password', is_active=True)

    def test_login_success_business_user(self):
        """Test successful login for BusinessUser and redirect to business dashboard"""
        login_data = {'username': 'business_user',
                      'password': 'business_password'}
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(response, reverse(
            'dashboard', kwargs={'user': 'business_user'}))

    def test_login_success_patron_user(self):
        """Test successful login for PatronUser and redirect to patron dashboard"""
        login_data = {'username': 'patron_user',
                      'password': 'patron_password'}
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(response, reverse(
            'dashboard', kwargs={'user': 'patron_user'}))

    def test_login_success_lipila_user(self):
        """Test successful login for LipilaUser and redirect to lipila dashboard"""
        login_data = {'username': 'lipila_user', 'password': 'lipila_password'}
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(response, reverse(
            'dashboard', kwargs={'user': 'lipila_user'}))

    def test_login_failure(self):
        """Test login failure with invalid credentials"""
        login_data = {'username': 'invalid_user',
                      'password': 'invalid_password'}
        response = self.client.post(reverse('login'), login_data)
        # Expect form to render again
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(
            str(messages[0]), "Your username and password didn't match")


class ContactViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_contact_success(self):
        """Test successful contact form submission"""
        valid_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message',
        }
        response = self.client.post(reverse('contact'), valid_data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(
            str(messages[0]), "Your message has been sent successfully")

    def test_contact_failure(self):
        """Test contact form submission with invalid data"""
        invalid_data = {'message': ''}  # Missing required fields
        response = self.client.post(reverse('contact'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Check form renders again
