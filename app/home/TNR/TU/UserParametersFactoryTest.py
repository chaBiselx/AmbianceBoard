from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from parameters import settings
from home.models.User import User
from home.factory.UserParametersFactory import UserParametersFactory
from home.enum.PermissionEnum import PermissionEnum
from django.contrib.contenttypes.models import ContentType
class UserParametersFactoryTest(TestCase):
    
    def setUp(self):
        # Créer un utilisateur standard
        self.standard_user = User.objects.create_user(
            username='standard_user',
            password='test123'
        )
        
        # Créer un utilisateur premium
        self.premium_user = User.objects.create_user(
            username='premium_user',
            password='test123'
        )
        
        # Ajouter les permissions premium
        self._add_premium_permissions(self.premium_user)
    
    def _add_premium_permissions(self, user):
        # Créer et ajouter toutes les permissions premium
        content_type = ContentType.objects.get_for_model(Permission)
        permissions = {
            PermissionEnum.USER_PREMIUM_OVER_LIMIT_SOUNDBOARD.name: 'Can have premium soundboard limit',
            PermissionEnum.USER_PREMIUM_OVER_LIMIT_PLAYLIST.name: 'Can have premium playlist limit',
            PermissionEnum.USER_PREMIUM_OVER_LIMIT_MUSIC_PER_PLAYLIST.name: 'Can have premium music per playlist limit',
            PermissionEnum.USER_PREMIUM_OVER_LIMIT_WEIGHT_MUSIC.name: 'Can have premium weight limit'
        }
        
        for codename, name in permissions.items():
            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=content_type,
                )
            except Permission.DoesNotExist:
                permission = Permission.objects.create(
                    codename=codename,
                    name=name,
                    content_type=content_type,
                )
            user.user_permissions.add(permission)
    
    def test_standard_user_limits(self):
        """Test que les limites standard sont correctement définies"""
        factory = UserParametersFactory(self.standard_user)
        
        self.assertEqual(factory.limit_soundboard, settings.LIMIT_USER_STANDARD_SOUNDBOARD)
        self.assertEqual(factory.limit_playlist, settings.LIMIT_USER_STANDARD_PLAYLIST)
        self.assertEqual(factory.limit_music_per_playlist, settings.LIMIT_USER_STANDARD_MUSIC_PER_PLAYLIST)
        self.assertEqual(factory.limit_weight_file, settings.LIMIT_USER_STANDARD_WEIGHT_MUSIC)
    
    def test_premium_user_limits(self):
        """Test que les limites premium sont correctement définies"""
        factory = UserParametersFactory(self.premium_user)
        
        self.assertEqual(factory.limit_soundboard, settings.LIMIT_USER_PREMIUM_SOUNDBOARD)
        self.assertEqual(factory.limit_playlist, settings.LIMIT_USER_PREMIUM_PLAYLIST)
        self.assertEqual(factory.limit_music_per_playlist, settings.LIMIT_USER_PREMIUM_MUSIC_PER_PLAYLIST)
        self.assertEqual(factory.limit_weight_file, settings.LIMIT_USER_PREMIUM_WEIGHT_MUSIC)
    
    def test_partial_premium_user(self):
        """Test qu'un utilisateur avec permissions premium partielles a les bonnes limites"""
        # Créer un utilisateur avec seulement certaines permissions premium
        partial_premium_user = User.objects.create_user(
            username='partial_premium',
            password='test123'
        )
        
        # Ajouter seulement la permission soundboard premium
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.create(
            codename=PermissionEnum.USER_PREMIUM_OVER_LIMIT_SOUNDBOARD.name,
            name='Can have premium soundboard limit',
            content_type=content_type,
        )
        partial_premium_user.user_permissions.add(permission)
        
        factory = UserParametersFactory(partial_premium_user)
        
        # Vérifier que seule la limite soundboard est premium
        self.assertEqual(factory.limit_soundboard, settings.LIMIT_USER_STANDARD_SOUNDBOARD)
        self.assertEqual(factory.limit_playlist, settings.LIMIT_USER_STANDARD_PLAYLIST)
        self.assertEqual(factory.limit_music_per_playlist, settings.LIMIT_USER_STANDARD_MUSIC_PER_PLAYLIST)
        self.assertEqual(factory.limit_weight_file, settings.LIMIT_USER_STANDARD_WEIGHT_MUSIC)
    
    def test_prefix_permission(self):
        """Test que le préfixe de permission est correct"""
        factory = UserParametersFactory(self.standard_user)
        self.assertEqual(factory.prefix_permission, "auth.")
    
    def test_initialization_order(self):
        """Test que les limites sont définies dans le bon ordre"""
        # Créer une sous-classe pour vérifier l'ordre d'appel
        class TestOrderFactory(UserParametersFactory):
            def __init__(self, user):
                self.call_order = []
                super().__init__(user)
                
            def _set_limit_soundboard(self):
                self.call_order.append('soundboard')
                super()._set_limit_soundboard()
                
            def _set_limit_playlist(self):
                self.call_order.append('playlist')
                super()._set_limit_playlist()
                
            def _set_limit_music_per_playlist(self):
                self.call_order.append('music_per_playlist')
                super()._set_limit_music_per_playlist()
                
            def _set_limit_weight_file(self):
                self.call_order.append('weight_file')
                super()._set_limit_weight_file()
        
        factory = TestOrderFactory(self.standard_user)
        expected_order = ['soundboard', 'playlist', 'music_per_playlist', 'weight_file']
        self.assertEqual(factory.call_order, expected_order)