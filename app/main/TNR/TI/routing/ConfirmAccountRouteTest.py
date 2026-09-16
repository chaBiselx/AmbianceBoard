"""
Test d'intégration pour la route: confirm account (/resend-email/confirm/<uuid_user>/<confirmation_token>)
"""
import uuid
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.domain.common.service.ConfirmationUserService import ConfirmationUserService

User = get_user_model()


@tag('integration')
class ConfirmAccountRouteTest(TestCase):
    """Tests pour la route confirm account"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )  # NOSONAR
        self.user.isConfirmed = False
        self.user.save()

    def test_confirm_account_with_valid_token_redirects_to_login(self):
        """Test qu'un token de confirmation valide confirme le compte et redirige vers login"""
        ConfirmationUserService(self.user).generation_uri()
        url = reverse('confirm_account', kwargs={
            'uuid_user': self.user.uuid,
            'confirmation_token': self.user.confirmationToken,
        })
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.isConfirmed)

    def test_confirm_account_with_invalid_token_returns_404(self):
        """Test qu'un token de confirmation invalide renvoie une erreur 404"""
        ConfirmationUserService(self.user).generation_uri()
        url = reverse('confirm_account', kwargs={
            'uuid_user': self.user.uuid,
            'confirmation_token': uuid.uuid4(),
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_confirm_account_with_unknown_user_returns_404(self):
        """Test qu'un utilisateur inconnu renvoie une erreur 404"""
        url = reverse('confirm_account', kwargs={
            'uuid_user': uuid.uuid4(),
            'confirmation_token': uuid.uuid4(),
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
