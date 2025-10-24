"""
Test d'intégration pour la route: send reset password (/reset-password)
"""
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
    
    def test_send_reset_password_accessible_without_auth(self):
        """Test que la route send reset password est accessible sans authentification"""
        response = self.client.get(reverse('send_reset_password'))
        self.assertIn(response.status_code, [200, 302])
    
