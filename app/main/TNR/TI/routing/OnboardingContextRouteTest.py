"""
Test d'intégration pour la route: onboarding context (/onboarding/context)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class OnboardingContextRouteTest(TestCase):
    """Tests pour la route onboarding context"""

    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )  # NOSONAR

    def test_onboardingcontext_accessible_without_auth(self):
        """Test que la route onboarding context est accessible sans authentification"""
        response = self.client.get(reverse('onboardingContext'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')

    def test_onboardingcontext_payload_structure_anonymous(self):
        """Test que le payload JSON contient les clés attendues pour un anonyme"""
        response = self.client.get(reverse('onboardingContext'))
        data = response.json()
        self.assertIn('locale', data)
        self.assertIn('labels', data)
        self.assertIn('urls', data)
        self.assertIn('steps', data)
        self.assertIn('feature_flags', data)
        self.assertIn('home', data['urls'])
        self.assertIn('login', data['urls'])
        self.assertNotIn('dashboard', data['urls'])

    def test_onboardingcontext_payload_structure_authenticated(self):
        """Test que le payload JSON contient des urls supplémentaires pour un utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('onboardingContext'))
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('dashboard', data['urls'])
        self.assertIn('settings', data['urls'])
