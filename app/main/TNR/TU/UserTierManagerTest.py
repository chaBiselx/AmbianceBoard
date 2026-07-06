from django.test import TestCase, tag
from django.contrib.auth.models import Group
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.UserTier import UserTier
from main.domain.common.utils.UserTierManager import UserTierManager
from main.domain.common.enum.GroupEnum import GroupEnum
from parameters import settings


@tag('unitaire')
class UserTierManagerTest(TestCase):

    def setUp(self):
        self.utilisateurStandard = 'Utilisateur Standard'
        self.standard_limits = settings.USER_TIERS['STANDARD']['limits']
        self.premium_limits = settings.USER_TIERS['PREMIUM_BASIC']['limits']

        # Créer les groupes nécessaires
        self.standard_group, _ = Group.objects.get_or_create(name=GroupEnum.USER_STANDARD.value)
        
        # Créer un utilisateur standard
        self.standard_user = User.objects.create_user(
            username='standard_user',
            password='test123' # NOSONAR
        )
        self.standard_user.groups.add(self.standard_group)
        
        # Créer un utilisateur premium
        self.premium_user = User.objects.create_user(
            username='premium_user',
            password='test123' # NOSONAR
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
        self.assertEqual(standard_limits['soundboard'], self.standard_limits['soundboard'])
        self.assertEqual(standard_limits['playlist'], self.standard_limits['playlist'])
        self.assertEqual(standard_limits['music_per_playlist'], self.standard_limits['music_per_playlist'])
        self.assertEqual(standard_limits['weight_music_mb'], self.standard_limits['weight_music_mb'])
        
        # Vérifier que les limites premium sont correctes
        self.assertEqual(premium_limits['soundboard'], self.premium_limits['soundboard'])
        self.assertEqual(premium_limits['playlist'], self.premium_limits['playlist'])
        self.assertEqual(premium_limits['music_per_playlist'], self.premium_limits['music_per_playlist'])
        self.assertEqual(premium_limits['weight_music_mb'], self.premium_limits['weight_music_mb'])
        
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
        self.assertEqual(standard_limits['soundboard'], self.standard_limits['soundboard'])
        self.assertEqual(standard_limits['playlist'], self.standard_limits['playlist'])
        
        # Vérifier les limites premium
        self.assertEqual(premium_limits['soundboard'], self.premium_limits['soundboard'])
        self.assertEqual(premium_limits['playlist'], self.premium_limits['playlist'])
    
    def test_user_limits_with_custom_tier(self):
        """Test les limites avec un tier personnalisé"""
        custom_user = User.objects.create_user(
            username='custom_user',
            password='test123' # NOSONAR
        )
        
        # Créer un tier avec des limites personnalisées
        UserTier.objects.create(
            user=custom_user,
            tier_name='STANDARD',
        )
        
        # Devrait retourner les limites effectives du tier
        user_tier = custom_user.tier_info
        effective_limits = user_tier.get_effective_limits()
        
        self.assertEqual(effective_limits['soundboard'], self.standard_limits['soundboard'])
        self.assertEqual(effective_limits['playlist'], self.standard_limits['playlist'])
    
    def test_can_user_create_methods(self):
        """Test les méthodes de vérification des capacités"""
        # Test soundboard
        self.assertTrue(UserTierManager.can_user_create_soundboard(self.standard_user, self.standard_limits['soundboard'] - 1))
        self.assertFalse(UserTierManager.can_user_create_soundboard(self.standard_user, self.standard_limits['soundboard']))
        
        # Test playlist
        self.assertTrue(UserTierManager.can_user_create_playlist(self.premium_user, self.premium_limits['playlist'] - 1))
        self.assertFalse(UserTierManager.can_user_create_playlist(self.premium_user, self.premium_limits['playlist']))
        
        # Test music per playlist
        self.assertTrue(UserTierManager.can_user_add_music_to_playlist(self.standard_user, self.standard_limits['music_per_playlist'] - 1))
        self.assertFalse(UserTierManager.can_user_add_music_to_playlist(self.standard_user, self.standard_limits['music_per_playlist']))
        
        # Test file size
        self.assertTrue(UserTierManager.can_user_upload_music_size(self.standard_user, self.standard_limits['weight_music_mb']))
        self.assertFalse(UserTierManager.can_user_upload_music_size(self.standard_user, self.standard_limits['weight_music_mb'] + 1))
    
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
        
        self.assertEqual(standard_limits['soundboard'], settings.USER_TIERS['STANDARD']['limits']['soundboard'])
        self.assertEqual(standard_limits['playlist'], settings.USER_TIERS['STANDARD']['limits']['playlist'])
        self.assertEqual(standard_limits['music_per_playlist'], settings.USER_TIERS['STANDARD']['limits']['music_per_playlist'])
        self.assertEqual(standard_limits['weight_music_mb'], settings.USER_TIERS['STANDARD']['limits']['weight_music_mb'])

        self.assertEqual(premium_limits['soundboard'], settings.USER_TIERS['PREMIUM_BASIC']['limits']['soundboard'])
        self.assertEqual(premium_limits['playlist'], settings.USER_TIERS['PREMIUM_BASIC']['limits']['playlist'])
        self.assertEqual(premium_limits['music_per_playlist'], settings.USER_TIERS['PREMIUM_BASIC']['limits']['music_per_playlist'])
        self.assertEqual(premium_limits['weight_music_mb'], settings.USER_TIERS['PREMIUM_BASIC']['limits']['weight_music_mb'])
