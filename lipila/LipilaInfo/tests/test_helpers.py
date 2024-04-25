from django.test import TestCase
import unittest
from django.db import models
from LipilaInfo.models import (
    ContactInfo, LipilaHome, LipilaUserEmail, Testimonial, LipilaUser)
from LipilaInfo.helpers import (
    get_lipila_contact_info,
    get_user_emails,
    get_lipila_home_page_info,
    get_testimonials,
)


class HelperFunctionTests(TestCase):

    def test_get_lipila_contact_info_success(self):
        ContactInfo.objects.create(
            street="Test Street",
            location="Test Location",
            phone1="123-456-7890",
            email1="test@example.com",
        )
        """Test get_lipila_contact_info returns contact info"""
        context = get_lipila_contact_info()
        self.assertIn('contact', context)
        self.assertIsInstance(context['contact'], ContactInfo)

    def test_get_lipila_contact_info_no_data(self):
        """Test get_lipila_contact_info with no ContactInfo"""
        context = get_lipila_contact_info()
        self.assertEqual(context, {})

    def test_get_user_emails(self):
        """Test get_user_emails returns all user emails"""
        LipilaUserEmail.objects.create(
            name="Test User",
            email="test@user.com",
            subject="Test subject",
            message="Test message",
        )
        context = get_user_emails()
        self.assertIn('user_messages', context)
        self.assertIsInstance(context['user_messages'], models.QuerySet)
        # Test data has 1 email
        self.assertEqual(context['user_messages'].count(), 1)


    def test_get_lipila_home_page_info_success(self):
        """Test get_lipila_home_page_info returns homepage info"""
        LipilaHome.objects.create(
            message="Test message",
            slogan="Test slogan",
        )  
        context = get_lipila_home_page_info()
        self.assertIn('lipila', context)
        self.assertIsInstance(context['lipila'], LipilaHome)
        self.assertEqual(context['lipila'].message, 'Test message')
        self.assertEqual(context['lipila'].slogan, 'Test slogan')

    def test_get_lipila_home_page_info_no_data(self):
        """Test get_lipila_home_page_info with no LipilaHome"""        
        context = get_lipila_home_page_info()
        self.assertEqual(context, {})

    def test_get_testimonials(self):
        """Test get_testimonials returns all testimonials"""
        lipila_user = LipilaUser.objects.create(username="test_user", password="test_password")
        Testimonial.objects.create(user=lipila_user
                                   ,message="Test testimonial",
        )
        context = get_testimonials()
        self.assertIn('testimonials', context)
        self.assertIsInstance(context['testimonials'], models.QuerySet)
        # Test data has 1 testimonial
        self.assertEqual(context['testimonials'].count(), 1)