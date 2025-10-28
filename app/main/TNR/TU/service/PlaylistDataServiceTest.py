"""
Tests unitaires pour le service PlaylistDataService.

Ce module teste le service responsable de la récupération
des données de configuration d'une playlist.
"""

from django.test import TestCase, tag
from unittest.mock import Mock, patch
from main.domain.common.service.PlaylistDataService import PlaylistDataService
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.FadePlaylistEnum import FadePlaylistEnum
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User


@tag('unitaire')
class PlaylistDataServiceTest(TestCase):
    """Tests pour le service PlaylistDataService"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.service = PlaylistDataService()
        self.user = User.objects.create(
            username="testuser",
            email="test@test.com"
        )

    @patch('main.domain.common.strategy.PlaylistStrategy.PlaylistStrategy.get_strategy')
    def test_get_playlist_data_returns_strategy_data(self, mock_get_strategy):
        """Test que le service retourne les données de la stratégie appropriée"""
        # Créer une mock strategy
        mock_strategy = Mock()
        expected_data = {
            'id': 'test-uuid',
            'type': 'MUSIC',
            'volume': 80,
            'delay': 5
        }
        mock_strategy.get_data.return_value = expected_data
        mock_get_strategy.return_value = mock_strategy

        # Créer une playlist
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test Playlist",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            volume=80
        )

        # Appeler le service
        result = self.service.get_playlist_data(playlist)

        # Vérifications
        mock_get_strategy.assert_called_once_with(PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name)
        mock_strategy.get_data.assert_called_once_with(playlist)
        self.assertEqual(result, expected_data)

    @patch('main.domain.common.strategy.PlaylistStrategy.PlaylistStrategy.get_strategy')
    def test_get_playlist_data_for_each_type(self, mock_get_strategy):
        """Test que le service gère correctement tous les types de playlist"""
        mock_strategy = Mock()
        mock_strategy.get_data.return_value = {'test': 'data'}
        mock_get_strategy.return_value = mock_strategy

        for playlist_type in PlaylistTypeEnum:
            playlist = Playlist.objects.create(
                user=self.user,
                name=f"Test {playlist_type.name}",
                typePlaylist=playlist_type.name
            )

            result = self.service.get_playlist_data(playlist)

            # Vérifier que la bonne stratégie a été demandée
            mock_get_strategy.assert_called_with(playlist_type.name)
            self.assertEqual(result, {'test': 'data'})

            # Réinitialiser pour le prochain test
            mock_get_strategy.reset_mock()
            mock_strategy.get_data.reset_mock()

    def test_service_uses_strategy_factory(self):
        """Test que le service utilise bien la fabrique de stratégies"""
        self.assertIsNotNone(self.service.strategy_factory)

    @patch('main.domain.common.strategy.PlaylistStrategy.PlaylistStrategy.get_strategy')
    def test_get_data_set(self, mock_get_strategy):
        """Test le service PlaylistDataService avec différents types de playlist"""
        # Créer une mock strategy qui retourne des données test
        mock_strategy = Mock()
        mock_strategy.get_data.return_value = {'test': 'data'}
        mock_get_strategy.return_value = mock_strategy
        
        # Test pour chaque type de playlist
        for playlist_type in PlaylistTypeEnum:
            playlist = Playlist.objects.create(
                user=self.user,
                name=f"Test {playlist_type.name}",
                typePlaylist=playlist_type.name
            )
            
            data = self.service.get_playlist_data(playlist)
            
            # Vérifier que la stratégie appropriée a été appelée
            mock_get_strategy.assert_called_with(playlist_type.name)
            self.assertEqual(data, {'test': 'data'})
            
            # Réinitialiser les mocks pour le prochain test
            mock_get_strategy.reset_mock()
            mock_strategy.get_data.reset_mock()

    def test_delay_should_be_zero_when_useSpecificDelay_false(self):
        """Vérifie que delay retourne 0 quand useSpecificDelay est False, sans fuite d'état d'une playlist précédente.

        Ce test reproduit un bug observé en production où le delay conserve une valeur > 0 alors que useSpecificDelay est False.
        Cause probable: mutation de l'objet default_data dans AbstractConfig.get_data (partagé entre instances) au lieu de travailler sur une copie.
        """
        # 1. Créer une playlist avec un délai spécifique
        playlist_with_delay = Playlist.objects.create(
            user=self.user,
            name="Playlist avec delay",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            useSpecificDelay=True,
            maxDelay=42
        )
        data_with_delay = self.service.get_playlist_data(playlist_with_delay)
        self.assertEqual(data_with_delay.get('delay'), 42, "Le délai spécifique devrait être 42")

        # 2. Créer une nouvelle playlist sans délai spécifique
        playlist_without_delay = Playlist.objects.create(
            user=self.user,
            name="Playlist sans delay",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            useSpecificDelay=False,
            maxDelay=999  # devrait être ignoré
        )
        data_without_delay = self.service.get_playlist_data(playlist_without_delay)

        # BUG attendu actuellement: data_without_delay['delay'] == 42 au lieu de 0
        self.assertEqual(
            data_without_delay.get('delay'),
            0,
            "Le délai ne doit pas hériter de la valeur précédente quand useSpecificDelay=False"
        )

    def test_fade_in_override_yes(self):
        """Test que fadeIn=YES active le fade même si la stratégie le désactive par défaut"""
        # Créer une playlist de type INSTANT (qui a fadeIn=False par défaut)
        # avec une surcharge YES
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test Instant avec fadeIn",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name,
            fadeIn=FadePlaylistEnum.YES.name
        )
        
        data = self.service.get_playlist_data(playlist)
        
        # Vérifier que fadeIn est activé malgré le défaut INSTANT
        self.assertTrue(data['fadeIn'], "fadeIn devrait être True avec surcharge YES")
        # La durée devrait rester celle par défaut de la stratégie (0 pour INSTANT)
        # mais le boolean fadeIn est à True

    def test_fade_in_override_no(self):
        """Test que fadeIn=NO désactive le fade même si la stratégie l'active par défaut"""
        # Créer une playlist de type MUSIC (qui a fadeIn=True par défaut)
        # avec une surcharge NO
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test Music sans fadeIn",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            fadeIn=FadePlaylistEnum.NO.name
        )
        
        data = self.service.get_playlist_data(playlist)
        
        # Vérifier que fadeIn est désactivé
        self.assertFalse(data['fadeIn'], "fadeIn devrait être False avec surcharge NO")
        # Et que la durée est mise à 0
        self.assertEqual(data['fadeInDuration'], 0, "fadeInDuration devrait être 0 quand fadeIn=NO")

    def test_fade_in_override_default(self):
        """Test que fadeIn=DEFAULT conserve la valeur de la stratégie"""
        # Créer une playlist de type MUSIC (qui a fadeIn=True par défaut)
        # avec la valeur DEFAULT
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test Music avec fadeIn par défaut",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            fadeIn=FadePlaylistEnum.DEFAULT.name
        )
        
        data = self.service.get_playlist_data(playlist)
        
        # Vérifier que fadeIn utilise la valeur par défaut de MUSIC (True)
        self.assertTrue(data['fadeIn'], "fadeIn devrait être True (valeur par défaut de MUSIC)")
        # Et que la durée est celle par défaut (5s pour MUSIC)
        self.assertEqual(data['fadeInDuration'], 5, "fadeInDuration devrait être 5s pour MUSIC")

    def test_fade_out_override_yes(self):
        """Test que fadeOut=YES active le fade même si la stratégie le désactive par défaut"""
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test Instant avec fadeOut",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name,
            fadeOut=FadePlaylistEnum.YES.name
        )
        
        data = self.service.get_playlist_data(playlist)
        
        self.assertTrue(data['fadeOut'], "fadeOut devrait être True avec surcharge YES")

    def test_fade_out_override_no(self):
        """Test que fadeOut=NO désactive le fade même si la stratégie l'active par défaut"""
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test Music sans fadeOut",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            fadeOut=FadePlaylistEnum.NO.name
        )
        
        data = self.service.get_playlist_data(playlist)
        
        self.assertFalse(data['fadeOut'], "fadeOut devrait être False avec surcharge NO")
        self.assertEqual(data['fadeOutDuration'], 0, "fadeOutDuration devrait être 0 quand fadeOut=NO")

    def test_fade_out_override_default(self):
        """Test que fadeOut=DEFAULT conserve la valeur de la stratégie"""
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test Ambient avec fadeOut par défaut",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name,
            fadeOut=FadePlaylistEnum.DEFAULT.name
        )
        
        data = self.service.get_playlist_data(playlist)
        
        self.assertTrue(data['fadeOut'], "fadeOut devrait être True (valeur par défaut de AMBIENT)")
        self.assertEqual(data['fadeOutDuration'], 3, "fadeOutDuration devrait être 3s pour AMBIENT")

    def test_both_fades_override(self):
        """Test que fadeIn et fadeOut peuvent être surchargés simultanément"""
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test avec les deux fades surchargés",
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            fadeIn=FadePlaylistEnum.NO.name,
            fadeOut=FadePlaylistEnum.YES.name
        )
        
        data = self.service.get_playlist_data(playlist)
        
        self.assertFalse(data['fadeIn'], "fadeIn devrait être False")
        self.assertTrue(data['fadeOut'], "fadeOut devrait être True")
        self.assertEqual(data['fadeInDuration'], 0)
        
    def tearDown(self):
        """Nettoyage après les tests"""
        Playlist.objects.all().delete()
        User.objects.all().delete()
