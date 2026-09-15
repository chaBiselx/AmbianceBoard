"""
Test d'intégration pour la route: Liste des soundboards publics de l'utilisateur pour les statistiques
(/public/stats/soundboards)
"""
from django.test import TestCase, Client, tag
from django.contrib.auth import get_user_model
from django.urls import reverse

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.UserTier import UserTier

User = get_user_model()


@tag('integration')
class ListPublicUserSoundboardsStatsRouteTest(TestCase):
    """Tests pour la route de liste des soundboards publics avec statistiques"""

    def setUp(self):
        self.client = Client()
        self.standard_user = User.objects.create_user(username='stats_list_standard', email='stats_list_standard@test.com', password='Test1234!')
        self.premium_user = User.objects.create_user(username='stats_list_premium', email='stats_list_premium@test.com', password='Test1234!')
        UserTier.objects.create(user=self.premium_user, tier_name='PREMIUM_BASIC')
        SoundBoard.objects.create(user=self.premium_user, name='SB Premium', is_public=True)

    def test_list_stats_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(reverse('ListPublicUserSoundboardsStats'))
        self.assertEqual(response.status_code, 302)

    def test_list_stats_forbidden_for_standard_tier(self):
        """Un utilisateur du tier STANDARD n'a pas accès aux statistiques"""
        self.client.login(username='stats_list_standard', password='Test1234!')
        response = self.client.get(reverse('ListPublicUserSoundboardsStats'))
        self.assertEqual(response.status_code, 403)

    def test_list_stats_accessible_for_premium_tier(self):
        """Un utilisateur premium a accès à la liste des statistiques"""
        self.client.login(username='stats_list_premium', password='Test1234!')
        response = self.client.get(reverse('ListPublicUserSoundboardsStats'))
        self.assertEqual(response.status_code, 200)
