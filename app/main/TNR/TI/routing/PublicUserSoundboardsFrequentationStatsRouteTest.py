"""
Test d'intégration pour la route: Statistiques de fréquentation d'un soundboard public
(/public/stats/soundboards/<uuid:soundboard_uuid>/frequentation)
"""
from django.test import TestCase, Client, tag
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
import json

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.UserTier import UserTier

User = get_user_model()


@tag('integration')
class PublicUserSoundboardsFrequentationStatsRouteTest(TestCase):
    """Tests pour la route de statistiques de fréquentation"""

    def setUp(self):
        self.client = Client()
        self.standard_user = User.objects.create_user(username='freq_standard', email='freq_standard@test.com', password='Test1234!')
        self.premium_user = User.objects.create_user(username='freq_premium', email='freq_premium@test.com', password='Test1234!')
        UserTier.objects.create(user=self.premium_user, tier_name='PREMIUM_BASIC')
        self.soundboard = SoundBoard.objects.create(user=self.premium_user, name='SB Frequentation', is_public=True)

    def test_frequentation_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(
            reverse('PublicUserSoundboardsFrequentationStats', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 302)

    def test_frequentation_forbidden_for_standard_tier(self):
        """Un utilisateur du tier STANDARD n'a pas accès aux statistiques de fréquentation"""
        self.client.login(username='freq_standard', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsFrequentationStats', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 403)

    def test_frequentation_returns_json_for_owner_premium(self):
        """Le propriétaire premium reçoit un JSON de données de fréquentation"""
        self.client.login(username='freq_premium', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsFrequentationStats', kwargs={'soundboard_uuid': self.soundboard.uuid}),
            {'period': 30}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('title', data)
        self.assertIn('data', data)

    def test_frequentation_with_invalid_uuid_returns_error(self):
        """Un UUID de soundboard inexistant doit produire une réponse d'erreur"""
        self.client.login(username='freq_premium', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsFrequentationStats', kwargs={'soundboard_uuid': uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertIn('error', data)
