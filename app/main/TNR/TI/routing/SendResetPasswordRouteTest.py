"""
Test d'intégration pour la route: send reset password (/reset-password)
"""
from unittest.mock import patch

from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class SendResetPasswordRouteTest(TestCase):
    """Tests pour la route send reset password"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()

    @patch('main.interface.ui.controller.general.generalViews.UserMail.send_reset_password_email')
    def test_send_reset_password_post_sends_email(self, mock_send_reset_password_email):
        """Test qu'un POST valide déclenche bien l'envoi de l'email de réinitialisation"""
        user = User.objects.create_user(
            username='reset-route-user',
            email='reset-route-user@test.com',
            password='password123',
        )

        response = self.client.post(reverse('send_reset_password'), {'identifier': user.username})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_send_reset_password_email.call_count, 1)
    
    def test_send_reset_password_accessible_without_auth(self):
        """Test que la route send reset password est accessible sans authentification"""
        response = self.client.get(reverse('send_reset_password'))
        self.assertIn(response.status_code, [200, 302])
    
