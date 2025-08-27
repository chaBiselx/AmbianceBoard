from django.test import TestCase
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from parameters import settings
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.UserTier import UserTier
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.enum.GroupEnum import GroupEnum
from main.utils.UserTierManager import UserTierManager


class UserParametersFactoryTest(TestCase):
    
    def setUp(self):
        # Créer les groupes nécessaires
        self.standard_group, _ = Group.objects.get_or_create(name=GroupEnum.USER_STANDARD.value)
        
        # Créer un utilisateur standard
        self.standard_user = User.objects.create_user(
            username='standard_user',
            password='test123'
        )
        self.standard_user.groups.add(self.standard_group)
        
        # Créer le tier pour l'utilisateur standard
        UserTier.objects.create(
            user=self.standard_user,
            tier_name='STANDARD'
        )
        
        # Créer un utilisateur premium
        self.premium_user = User.objects.create_user(
            username='premium_user',
            password='test123'
        )
        # Créer le tier pour l'utilisateur premium
        UserTier.objects.create(
            user=self.premium_user,
            tier_name='PREMIUM_BASIC'
        )
        
    def test_standard_user_limits(self):
        """Test que les limites standard sont correctement définies"""
        factory = UserParametersFactory(self.standard_user)
        
        standard_limits = UserTierManager.get_tier_limits('STANDARD')
        self.assertEqual(factory.limit_soundboard, standard_limits['soundboard'])
        self.assertEqual(factory.limit_playlist, standard_limits['playlist'])
        self.assertEqual(factory.limit_music_per_playlist, standard_limits['music_per_playlist'])
        self.assertEqual(factory.limit_weight_file, standard_limits['weight_music_mb'])
    
    def test_premium_user_limits(self):
        """Test que les limites premium sont correctement définies"""

        factory = UserParametersFactory(self.premium_user)
        
        premium_limits = UserTierManager.get_tier_limits('PREMIUM_BASIC')
        self.assertEqual(factory.limit_soundboard, premium_limits['soundboard'])
        self.assertEqual(factory.limit_playlist, premium_limits['playlist'])
        self.assertEqual(factory.limit_music_per_playlist, premium_limits['music_per_playlist'])
        self.assertEqual(factory.limit_weight_file, premium_limits['weight_music_mb'])
    
    def test_user_without_tier(self):
        """Test qu'un utilisateur sans tier obtient les limites standard"""
        user_no_tier = User.objects.create_user(
            username='no_tier_user',
            password='test123'
        )
        
        factory = UserParametersFactory(user_no_tier)
        
        standard_limits = UserTierManager.get_tier_limits('STANDARD')
        self.assertEqual(factory.limit_soundboard, standard_limits['soundboard'])
        self.assertEqual(factory.limit_playlist, standard_limits['playlist'])
        self.assertEqual(factory.limit_music_per_playlist, standard_limits['music_per_playlist'])
        self.assertEqual(factory.limit_weight_file, standard_limits['weight_music_mb'])
    
    def test_tier_properties(self):
        """Test que les propriétés de tier fonctionnent correctement"""
        factory = UserParametersFactory(self.premium_user)

        self.assertEqual(factory.user_tier_name, 'PREMIUM_BASIC')
        self.assertEqual(factory.user_tier_display_name, UserTierManager.get_tier_display_name('PREMIUM_BASIC'))
    
    def test_user_tier_manager_integration(self):
        """Test l'intégration avec UserTierManager"""
        factory = UserParametersFactory(self.premium_user)
        
        # Vérifier que les limites correspondent à celles du UserTierManager
        manager_limits = UserTierManager.get_user_limits(self.premium_user)
        self.assertEqual(factory.limit_soundboard, manager_limits['soundboard'])
        self.assertEqual(factory.limit_playlist, manager_limits['playlist'])
        self.assertEqual(factory.limit_music_per_playlist, manager_limits['music_per_playlist'])
        self.assertEqual(factory.limit_weight_file, manager_limits['weight_music_mb'])