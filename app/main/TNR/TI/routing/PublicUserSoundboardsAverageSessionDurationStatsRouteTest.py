"""
Test d'intégration pour la route: Statistiques de durée moyenne de session d'un soundboard public
(/public/stats/soundboards/<uuid:soundboard_uuid>/moyenne)
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
class PublicUserSoundboardsAverageSessionDurationStatsRouteTest(TestCase):
    """Tests pour la route de statistiques de durée moyenne de session"""

    def setUp(self):
        self.client = Client()
        self.standard_user = User.objects.create_user(username='avgdur_standard', email='avgdur_standard@test.com', password='Test1234!')
        self.premium_user = User.objects.create_user(username='avgdur_premium', email='avgdur_premium@test.com', password='Test1234!')
        UserTier.objects.create(user=self.premium_user, tier_name='PREMIUM_BASIC')
        self.soundboard = SoundBoard.objects.create(user=self.premium_user, name='SB Avg Duration', is_public=True)

    def test_average_duration_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(
            reverse('PublicUserSoundboardsAverageSessionDurationStats', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 302)

    def test_average_duration_forbidden_for_standard_tier(self):
        """Un utilisateur du tier STANDARD n'a pas accès à ces statistiques"""
        self.client.login(username='avgdur_standard', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsAverageSessionDurationStats', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 403)

    def test_average_duration_returns_json_for_owner_premium(self):
        """Le propriétaire premium reçoit un JSON de données de durée moyenne de session"""
        self.client.login(username='avgdur_premium', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsAverageSessionDurationStats', kwargs={'soundboard_uuid': self.soundboard.uuid}),
            {'period': 30}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('title', data)
        self.assertIn('data', data)

    def test_average_duration_with_invalid_uuid_returns_error(self):
        """Un UUID de soundboard inexistant doit produire une réponse d'erreur"""
        self.client.login(username='avgdur_premium', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsAverageSessionDurationStats', kwargs={'soundboard_uuid': uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertIn('error', data)
