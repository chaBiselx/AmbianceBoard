"""
Test d'intégration pour la route: Statistiques d'un soundboard public
(/public/stats/soundboards/<uuid:soundboard_uuid>)
"""
from django.test import TestCase, Client, tag
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.UserTier import UserTier

User = get_user_model()


@tag('integration')
class PublicUserSoundboardsStatsRouteTest(TestCase):
    """Tests pour la route de statistiques d'un soundboard public"""

    def setUp(self):
        self.client = Client()
        self.standard_user = User.objects.create_user(username='stats_owner_standard', email='stats_owner_standard@test.com', password='Test1234!')
        self.premium_user = User.objects.create_user(username='stats_owner_premium', email='stats_owner_premium@test.com', password='Test1234!')
        self.other_premium_user = User.objects.create_user(username='stats_other_premium', email='stats_other_premium@test.com', password='Test1234!')
        UserTier.objects.create(user=self.premium_user, tier_name='PREMIUM_BASIC')
        UserTier.objects.create(user=self.other_premium_user, tier_name='PREMIUM_BASIC')
        self.soundboard = SoundBoard.objects.create(user=self.premium_user, name='SB Stats', is_public=True)

    def test_stats_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(
            reverse('PublicUserSoundboardsStats', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 302)

    def test_stats_forbidden_for_standard_tier(self):
        """Un utilisateur du tier STANDARD n'a pas accès aux statistiques"""
        self.client.login(username='stats_owner_standard', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsStats', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 403)

    def test_stats_accessible_for_owner_premium(self):
        """Le propriétaire premium peut accéder aux statistiques de son soundboard"""
        self.client.login(username='stats_owner_premium', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsStats', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)

    def test_stats_not_found_for_non_owner(self):
        """Un autre utilisateur premium ne peut pas voir les statistiques d'un soundboard qui ne lui appartient pas"""
        self.client.login(username='stats_other_premium', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsStats', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 404)

    def test_stats_with_invalid_uuid(self):
        """Test avec un UUID de soundboard inexistant"""
        self.client.login(username='stats_owner_premium', password='Test1234!')
        response = self.client.get(
            reverse('PublicUserSoundboardsStats', kwargs={'soundboard_uuid': uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)
