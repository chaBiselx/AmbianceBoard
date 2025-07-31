# RGPDServiceNotConfirmedTest.py
import datetime
from django.test import TestCase
from main.models.User import User
from main.service.cron.RGPDService import RGPDService
from django.utils.timezone import make_aware

class RGPDServiceNotConfirmedTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com')
        self.user1.isConfirmed = False
        self.user1.demandeConfirmationDate = make_aware(datetime.datetime.now() - datetime.timedelta(days=21))
        self.user1.save()

        self.user2 = User.objects.create_user(username='user2', email='user2@example.com')
        self.user2.isConfirmed = True
        self.user2.save()

    def test_prevent_not_confirmed(self):
        RGPDService().prevent_not_confirmed()
        self.assertTrue(User.objects.filter(username='user1').exists())
        self.assertTrue(User.objects.filter(username='user2').exists())

    def test_prevent_not_confirmed_user_not_confirmed(self):
        user3 = User.objects.create_user(username='user3', email='user3@example.com')
        user3.isConfirmed = False
        user3.demandeConfirmationDate = make_aware(datetime.datetime.now() - datetime.timedelta(days=35))
        user3.save()

        RGPDService().prevent_not_confirmed()
        self.assertTrue(User.objects.filter(username='user3').exists())

    def test_prevent_not_confirmed_user_confirmed(self):
        user4 = User.objects.create_user(username='user4', email='user4@example.com')
        user4.isConfirmed = True
        user4.save()

        RGPDService().prevent_not_confirmed()
        self.assertTrue(User.objects.filter(username='user4').exists())
        
    def test_delete_not_confirmed(self):
        RGPDService().delete_not_confirmed()
        self.assertTrue(User.objects.filter(username='user1').exists())
        self.assertTrue(User.objects.filter(username='user2').exists())

    def test_delete_not_confirmed_user_not_confirmed(self):
        user3 = User.objects.create_user(username='user3', email='user3@example.com')
        user3.isConfirmed = False
        user3.demandeConfirmationDate = make_aware(datetime.datetime.now() - datetime.timedelta(days=181))
        user3.save()

        RGPDService().delete_not_confirmed()
        self.assertFalse(User.objects.filter(username='user3').exists())

    def test_delete_not_confirmed_user_confirmed(self):
        user4 = User.objects.create_user(username='user4', email='user4@example.com')
        user4.isConfirmed = True
        user4.save()

        RGPDService().delete_not_confirmed()
        self.assertTrue(User.objects.filter(username='user4').exists())