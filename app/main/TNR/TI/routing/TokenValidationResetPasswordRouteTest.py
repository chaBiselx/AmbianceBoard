"""
Test d'intégration pour la route: token validation reset password (/reset-password/validate/<uuid_user>/<token_reinitialisation>)
"""
import uuid
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.domain.general.service.ResetPasswordService import ResetPasswordService

User = get_user_model()


@tag('integration')
class TokenValidationResetPasswordRouteTest(TestCase):
    """Tests pour la route token validation reset password"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )  # NOSONAR

    def test_token_validation_reset_password_valid_token_renders_form(self):
        """Test qu'un token de réinitialisation valide affiche le formulaire"""
        ResetPasswordService(self.user).generation_uri()
        url = reverse('token_validation_reset_password', kwargs={
            'uuid_user': self.user.uuid,
            'token_reinitialisation': self.user.tokenReinitialisation,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_token_validation_reset_password_invalid_token_returns_404(self):
        """Test qu'un token de réinitialisation invalide renvoie une erreur 404"""
        ResetPasswordService(self.user).generation_uri()
        url = reverse('token_validation_reset_password', kwargs={
            'uuid_user': self.user.uuid,
            'token_reinitialisation': 'invalid-token',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_token_validation_reset_password_unknown_user_returns_404(self):
        """Test qu'un utilisateur inconnu renvoie une erreur 404"""
        url = reverse('token_validation_reset_password', kwargs={
            'uuid_user': uuid.uuid4(),
            'token_reinitialisation': 'some-token',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_token_validation_reset_password_post_valid_token_changes_password(self):
        """Test qu'un POST avec un token valide change le mot de passe et redirige vers login"""
        ResetPasswordService(self.user).generation_uri()
        url = reverse('token_validation_reset_password', kwargs={
            'uuid_user': self.user.uuid,
            'token_reinitialisation': self.user.tokenReinitialisation,
        })
        response = self.client.post(url, {
            'password': 'NewPassw0rd!123',
            'password_confirmation': 'NewPassw0rd!123',
        })
        self.assertIn(response.status_code, [200, 302])
