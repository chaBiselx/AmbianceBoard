"""
Test d'intégration pour la route: resend email confirmation (/resend-email/)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class ResendEmailConfirmationRouteTest(TestCase):
    """Tests pour la route resend email confirmation"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
    
    def test_resend_email_confirmation_accessible_without_auth(self):
        """Test que la route resend email confirmation est accessible sans authentification"""
        response = self.client.get(reverse('resend_email_confirmation'))
        self.assertIn(response.status_code, [200, 302])
    
