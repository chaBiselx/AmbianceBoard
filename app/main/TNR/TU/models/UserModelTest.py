from django.test import TestCase
from main.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError


class UserModelTest(TestCase):
    def test_checkBanned(self):
        # Créer un utilisateur non banni
        user = User.objects.create(username='testuser', email='test@example.com')
        self.assertFalse(user.checkBanned())

        # Créer un utilisateur banni avec une date d'expiration dans 1 jour
        expiration_date = timezone.make_aware(datetime.now() + timedelta(days=1))
       
        user = User.objects.create(username='testuser2', email='test2@example.com', isBan=True, banExpiration=expiration_date)
        self.assertTrue(user.checkBanned())

        # Créer un utilisateur banni sans date d'expiration
        user = User.objects.create(username='testuser3', email='test3@example.com', isBan=True)
        self.assertTrue(user.checkBanned())

        # Créer un utilisateur non banni avec une date d'expiration dans 1 jour
        expiration_date = timezone.make_aware(datetime.now() + timedelta(days=1))
        user = User.objects.create(username='testuser4', email='test4@example.com', banExpiration=expiration_date)
        self.assertFalse(user.checkBanned())

    def test_checkBanned_with_expired_ban(self):
        # Créer un utilisateur banni avec une date d'expiration dépassée
        expiration_date = timezone.make_aware(datetime.now() - timedelta(days=1))
        user = User.objects.create(username='testuser5', email='test5@example.com', isBan=True, banExpiration=expiration_date)
        self.assertFalse(user.checkBanned())

    def test_checkBanned_with_invalid_ban_expiration(self):
        # Créer un utilisateur banni avec une date d'expiration invalide
        user = User(username='testuser6', email='test6@example.com', isBan=True, banExpiration='invalid_date')
        with self.assertRaises(ValidationError):
            user.full_clean()