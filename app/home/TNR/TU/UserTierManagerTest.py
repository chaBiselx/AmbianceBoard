from django.test import TestCase
from django.contrib.auth.models import Group
from home.models.User import User
from home.models.UserTier import UserTier
from home.utils.UserTierManager import UserTierManager
from home.enum.GroupEnum import GroupEnum
from parameters import settings


class UserTierManagerTest(TestCase):
    self.utilisateurStandard = 'Utilisateur Standard'
    
    def setUp(self):
        # Créer les groupes nécessaires
        self.standard_group, _ = Group.objects.get_or_create(name=GroupEnum.USER_STANDARD.value)
        
        # Créer un utilisateur standard
        self.standard_user = User.objects.create_user(
            username='standard_user',
            password='test123'
        )
        self.standard_user.groups.add(self.standard_group)
        
        # Créer un utilisateur premium
        self.premium_user = User.objects.create_user(
            username='premium_user',
            password='test123'
        )
        
        # Créer les tiers correspondants
        UserTier.objects.create(
            user=self.standard_user,
            tier_name='STANDARD'
        )
        
        UserTier.objects.create(
            user=self.premium_user,
            tier_name='PREMIUM_BASIC'
        )
    
    def test_get_all_tiers(self):
        """Test que tous les tiers sont retournés"""
        tiers = UserTierManager.get_all_tiers()
        
        self.assertIn('STANDARD', tiers)
        self.assertIn('PREMIUM_BASIC', tiers)
        self.assertEqual(tiers['STANDARD']['display_name'], self.utilisateurStandard)
        self.assertEqual(tiers['PREMIUM_BASIC']['display_name'], 'Premium Basique')
    
    def test_get_tier_info(self):
        """Test la récupération d'informations sur un tier"""
        standard_info = UserTierManager.get_tier_info('STANDARD')
        premium_info = UserTierManager.get_tier_info('PREMIUM_BASIC')
        invalid_info = UserTierManager.get_tier_info('INVALID')
        
        self.assertIsNotNone(standard_info)
        self.assertIsNotNone(premium_info)
        self.assertIsNone(invalid_info)
        
        self.assertEqual(standard_info['name'], 'Standard')
        self.assertEqual(premium_info['name'], 'Premium Basic')
    
    def test_get_tier_limits(self):
        """Test la récupération des limites d'un tier"""
        standard_limits = UserTierManager.get_tier_limits('STANDARD')
        premium_limits = UserTierManager.get_tier_limits('PREMIUM_BASIC')
        invalid_limits = UserTierManager.get_tier_limits('INVALID')
        
        # Vérifier que les limites standard sont correctes
        self.assertEqual(standard_limits['soundboard'], 5)
        self.assertEqual(standard_limits['playlist'], 75)
        self.assertEqual(standard_limits['music_per_playlist'], 10)
        self.assertEqual(standard_limits['weight_music_mb'], 50)
        
        # Vérifier que les limites premium sont correctes
        self.assertEqual(premium_limits['soundboard'], 25)
        self.assertEqual(premium_limits['playlist'], 1000)
        self.assertEqual(premium_limits['music_per_playlist'], 25)
        self.assertEqual(premium_limits['weight_music_mb'], 120)
        
        # Vérifier que les limites invalides retournent standard
        self.assertEqual(invalid_limits, standard_limits)
    
    def test_get_tier_display_name(self):
        """Test la récupération du nom d'affichage"""
        standard_name = UserTierManager.get_tier_display_name('STANDARD')
        premium_name = UserTierManager.get_tier_display_name('PREMIUM_BASIC')
        invalid_name = UserTierManager.get_tier_display_name('INVALID')
        
        self.assertEqual(standard_name, self.utilisateurStandard)
        self.assertEqual(premium_name, 'Premium Basique')
        self.assertEqual(invalid_name, self.utilisateurStandard)  # Fallback
    
    def test_get_user_limits(self):
        """Test la récupération des limites d'un utilisateur"""
        standard_limits = UserTierManager.get_user_limits(self.standard_user)
        premium_limits = UserTierManager.get_user_limits(self.premium_user)
        
        # Vérifier les limites standard
        self.assertEqual(standard_limits['soundboard'], 5)
        self.assertEqual(standard_limits['playlist'], 75)
        
        # Vérifier les limites premium
        self.assertEqual(premium_limits['soundboard'], 25)
        self.assertEqual(premium_limits['playlist'], 1000)
    
    def test_user_limits_with_custom_tier(self):
        """Test les limites avec un tier personnalisé"""
        custom_user = User.objects.create_user(
            username='custom_user',
            password='test123'
        )
        
        # Créer un tier avec des limites personnalisées
        UserTier.objects.create(
            user=custom_user,
            tier_name='STANDARD',
        )
        
        # Devrait retourner les limites effectives du tier
        user_tier = custom_user.tier_info
        effective_limits = user_tier.get_effective_limits()
        
        self.assertEqual(effective_limits['soundboard'], 15)
        self.assertEqual(effective_limits['playlist'], 200)
    
    def test_can_user_create_methods(self):
        """Test les méthodes de vérification des capacités"""
        # Test soundboard
        self.assertTrue(UserTierManager.can_user_create_soundboard(self.standard_user, 4))
        self.assertFalse(UserTierManager.can_user_create_soundboard(self.standard_user, 5))
        
        # Test playlist
        self.assertTrue(UserTierManager.can_user_create_playlist(self.premium_user, 999))
        self.assertFalse(UserTierManager.can_user_create_playlist(self.premium_user, 1000))
        
        # Test music per playlist
        self.assertTrue(UserTierManager.can_user_add_music_to_playlist(self.standard_user, 9))
        self.assertFalse(UserTierManager.can_user_add_music_to_playlist(self.standard_user, 10))
        
        # Test file size
        self.assertTrue(UserTierManager.can_user_upload_music_size(self.standard_user, 49))
        self.assertFalse(UserTierManager.can_user_upload_music_size(self.standard_user, 51))
    
    def test_get_tier_comparison(self):
        """Test la comparaison des tiers"""
        comparison = UserTierManager.get_tier_comparison()
        
        self.assertIn('STANDARD', comparison)
        self.assertIn('PREMIUM_BASIC', comparison)
        
        standard_comp = comparison['STANDARD']
        self.assertEqual(standard_comp['display_name'], self.utilisateurStandard)
        self.assertIn('limits', standard_comp)
    
    def test_compatibility_with_settings(self):
        """Test la compatibilité avec les anciennes constantes settings"""
        # Vérifier que les nouvelles fonctions retournent les mêmes valeurs
        # que les anciennes constantes
        standard_limits = UserTierManager.get_tier_limits('STANDARD')
        premium_limits = UserTierManager.get_tier_limits('PREMIUM_BASIC')
        
        self.assertEqual(standard_limits['soundboard'], -1)
        self.assertEqual(standard_limits['playlist'], -1)
        self.assertEqual(standard_limits['music_per_playlist'], -1)
        self.assertEqual(standard_limits['weight_music_mb'], -1)

        self.assertEqual(premium_limits['soundboard'], -1)
        self.assertEqual(premium_limits['playlist'], -1)
        self.assertEqual(premium_limits['music_per_playlist'], -1)
        self.assertEqual(premium_limits['weight_music_mb'], -1)
