"""
Test d'intégration pour la route: onboarding context (/onboarding/context)
"""
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

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

    @patch('main.domain.general.service.OnboardingContextService.SoundBoardRepository.get_public_not_banned_with_min_tracks')
    def test_authenticated_payload_includes_soundboard_feature_steps(self, get_public_soundboard):
        self.client.login(username='testuser', password='testpass123')
        get_public_soundboard.return_value = SimpleNamespace(uuid=uuid4(), user_id=self.user.id + 1)

        response = self.client.get(reverse('onboardingContext'))
        steps = {step['id']: step for step in response.json()['steps']}

        self.assertIn('private_propose_playlist', steps)
        self.assertIn('private_share_listening', steps)
        self.assertIn('public_playing_monitor', steps)
        self.assertEqual(steps['private_propose_playlist']['selector'], '[data-shepherd="propose-playlist"]')
        self.assertEqual(steps['private_share_listening']['selector'], '[data-shepherd="share-listening"]')
        self.assertEqual(steps['public_playing_monitor']['selector'], '[data-shepherd="playing-monitor"]')
        self.assertTrue(all(steps[step_id]['title'] and steps[step_id]['description'] for step_id in (
            'private_propose_playlist',
            'private_share_listening',
            'public_playing_monitor',
        )))
