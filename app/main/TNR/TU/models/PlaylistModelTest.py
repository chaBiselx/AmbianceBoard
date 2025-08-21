from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock
import uuid
from main.models.Playlist import Playlist
from main.models.User import User
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

playlist_name = "Test Playlist"

class PlaylistModelTest(TestCase):
    def setUp(self):
        """Initialisation des données de test"""
        self.user = User.objects.create(
            username="testuser",
            email="test@test.com"
        )
        
        # Créer un faux fichier pour les tests
        self.test_icon = SimpleUploadedFile(
            name='test_icon.png',
            content=b'file_content',
            content_type='image/png'
        )
        
    def test_playlist_creation_basic(self):
        """Test la création basique d'une Playlist"""
        playlist = Playlist.objects.create(
            user=self.user,
            name=playlist_name,
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        
        self.assertTrue(isinstance(playlist, Playlist))
        self.assertEqual(playlist.name, playlist_name)
        self.assertEqual(playlist.typePlaylist, PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name)
        self.assertEqual(playlist.color, "#000000")  # Valeur par défaut
        self.assertEqual(playlist.colorText, "#ffffff")  # Valeur par défaut
        self.assertEqual(playlist.volume, 75)  # Valeur par défaut

    def test_volume_validators(self):
        """Test les validateurs de volume"""
        # Test volume trop bas
        with self.assertRaises(ValidationError):
            playlist = Playlist.objects.create(
                user=self.user,
                name=playlist_name,
                typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
                volume=-1
            )
            playlist.full_clean()
            
        # Test volume trop haut
        with self.assertRaises(ValidationError):
            playlist = Playlist.objects.create(
                user=self.user,
                name=playlist_name,
                typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
                volume=101
            )
            playlist.full_clean()
            
        # Test volume valide
        playlist = Playlist.objects.create(
            user=self.user,
            name=playlist_name,
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            volume=50
        )
        playlist.full_clean()  # Ne devrait pas lever d'exception

    def test_user_required(self):
        """Test que l'utilisateur est obligatoire"""
        with self.assertRaises(ValueError):
            Playlist.objects.create(
                name=playlist_name,
                typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
            )
            
    @patch('uuid.uuid4')
    @patch('main.message.ReduceSizeImgMessenger.reduce_size_img.apply_async')
    def test_icon_upload_on_create(self, mock_reduce_size, mock_uuid):
        """Test le téléchargement et le traitement de l'icône lors de la création"""
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_uuid.return_value = uuid.UUID(test_uuid)
        
        # Créer d'abord la Playlist sans icône
        playlist = Playlist.objects.create(
            user=self.user,
            name=playlist_name,
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            icon=self.test_icon
        )
        
        # Vérifier que le nom du fichier a été modifié
        self.assertTrue(playlist.icon.name.endswith('.png'))
        
        # Vérifier que la tâche de redimensionnement a été appelée
        mock_reduce_size.assert_called_once_with(
            args=['Playlist', playlist.id],
            queue='default',
            priority=1
        )

    @patch('uuid.uuid4')
    @patch('main.message.ReduceSizeImgMessenger.reduce_size_img.apply_async')
    def test_icon_upload_on_update(self, mock_reduce_size, mock_uuid):
        """Test le téléchargement et le traitement de l'icône lors de la mise à jour"""
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_uuid.return_value = uuid.UUID(test_uuid)
        
        # Créer d'abord la Playlist sans icône
        playlist = Playlist.objects.create(
            user=self.user,
            name=playlist_name,
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        
        # Ensuite, ajouter l'icône
        playlist.icon = self.test_icon
        playlist.clean()  # Important pour définir _icon_changed
        playlist.save()
        
        # Vérifier que le nom du fichier a été modifié
        self.assertTrue(playlist.icon.name.endswith('.png'))
        
        # Vérifier que la tâche de redimensionnement a été appelée
        mock_reduce_size.assert_called_once_with(
            args=['Playlist', playlist.id],
            queue='default',
            priority=1
        )

    @patch('main.strategy.PlaylistStrategy.PlaylistStrategy.get_strategy')
    def test_get_data_set(self, mock_get_strategy):
        """Test la méthode get_data_set avec différents types de playlist"""
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
            
            data = playlist.get_data_set()
            
            # Vérifier que la stratégie appropriée a été appelée
            mock_get_strategy.assert_called_with(playlist_type.name)
            self.assertEqual(data, {'test': 'data'})
            
            # Réinitialiser les mocks pour le prochain test
            mock_get_strategy.reset_mock()
            mock_strategy.get_data.reset_mock()

    def test_playlist_types(self):
        """Test la validation des types de playlist"""
        for playlist_type in PlaylistTypeEnum:
            playlist = Playlist.objects.create(
                user=self.user,
                name=f"Test {playlist_type.name}",
                typePlaylist=playlist_type.name
            )
            self.assertEqual(playlist.typePlaylist, playlist_type.name)
        
        # Test avec un type invalide
        with self.assertRaises(ValidationError):
            playlist = Playlist.objects.create(
                user=self.user,
                name="Test Invalid",
                typePlaylist="INVALID_TYPE"
            )
            playlist.full_clean()

    def test_user_deletion_cascade(self):
        """Test que la suppression d'un utilisateur supprime ses playlists"""
        playlist = Playlist.objects.create(
            user=self.user,
            name=playlist_name,
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        
        _ = self.user.uuid
        self.user.delete()
        
        # Vérifier que la playlist a été supprimée
        with self.assertRaises(Playlist.DoesNotExist):
            Playlist.objects.get(uuid=playlist.uuid)

    def tearDown(self):
        """Nettoyage après les tests"""
        # Supprimer les fichiers créés pendant les tests
        for playlist in Playlist.objects.all():
            if playlist.icon:
                storage = playlist.icon.storage
                if storage.exists(playlist.icon.name):
                    storage.delete(playlist.icon.name)