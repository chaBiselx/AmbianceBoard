from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock, Mock
import uuid
from main.service.RandomizeTrackService import RandomizeTrackService
from main.service.SoundBoardService import SoundBoardService
from main.models.Music import Music
from main.models.Track import Track
from main.models.Playlist import Playlist
from main.models.User import User
from main.models.SoundBoard import SoundBoard
from main.filters.MusicFilter import MusicFilter

class RandomizeTrackServiceTest(TestCase):
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.factory = RequestFactory()
        self.user = Mock()
        self.user.id = 1
        self.request = self.factory.get('/')
        self.request.user = self.user
        self.service = RandomizeTrackService(self.request)
        self.playlist_uuid = uuid.uuid4()
        self.soundboard_uuid = uuid.uuid4()
        self.token = "test_token"
        self.music_id = 1

    def test_init(self):
        """Test l'initialisation du service"""
        service = RandomizeTrackService(self.request)
        self.assertEqual(service.request, self.request)

    @patch('main.service.RandomizeTrackService.MusicFilter')
    @patch('main.service.RandomizeTrackService.RandomizeTrackService._get_random_music_from_playlist')
    def test_generate_private_success(self, mock_get_random, mock_music_filter):
        """Test génération aléatoire privée avec succès"""
        # Arrange
        mock_music = Mock(spec=Music)
        mock_filter_instance = Mock()
        mock_music_filter.return_value = mock_filter_instance
        mock_get_random.return_value = mock_music
        
        # Act
        result = self.service.generate_private(self.playlist_uuid)
        
        # Assert
        self.assertEqual(result, mock_music)
        mock_music_filter.assert_called_once()
        mock_filter_instance.filter_by_user.assert_called_once_with(self.user)
        mock_get_random.assert_called_once_with(mock_filter_instance, self.playlist_uuid)

    @patch('main.service.RandomizeTrackService.MusicFilter')
    @patch('main.service.RandomizeTrackService.RandomizeTrackService._get_random_music_from_playlist')
    def test_generate_private_playlist_not_exist(self, mock_get_random, mock_music_filter):
        """Test génération aléatoire privée quand la playlist n'existe pas"""
        # Arrange
        mock_filter_instance = Mock()
        mock_music_filter.return_value = mock_filter_instance
        mock_get_random.side_effect = Playlist.DoesNotExist()
        
        # Act
        result = self.service.generate_private(self.playlist_uuid)
        
        # Assert
        self.assertIsNone(result)

    @patch('main.service.RandomizeTrackService.SoundBoardService')
    @patch('main.service.RandomizeTrackService.MusicFilter')
    @patch('main.service.RandomizeTrackService.RandomizeTrackService._get_random_music_from_playlist')
    def test_generate_public_success(self, mock_get_random, mock_music_filter, mock_soundboard_service):
        """Test génération aléatoire publique avec succès"""
        # Arrange
        mock_soundboard = Mock(spec=SoundBoard)
        mock_music = Mock(spec=Music)
        mock_service_instance = Mock()
        mock_filter_instance = Mock()
        
        mock_soundboard_service.return_value = mock_service_instance
        mock_service_instance.get_public_soundboard.return_value = mock_soundboard
        mock_music_filter.return_value = mock_filter_instance
        mock_get_random.return_value = mock_music
        
        # Act
        result = self.service.generate_public(self.soundboard_uuid, self.playlist_uuid)
        
        # Assert
        self.assertEqual(result, mock_music)
        mock_soundboard_service.assert_called_once_with(self.request)
        mock_service_instance.get_public_soundboard.assert_called_once_with(self.soundboard_uuid)
        mock_music_filter.assert_called_once()
        mock_get_random.assert_called_once_with(mock_filter_instance, self.playlist_uuid)

    @patch('main.service.RandomizeTrackService.SoundBoardService')
    def test_generate_public_soundboard_not_found(self, mock_soundboard_service):
        """Test génération aléatoire publique quand le soundboard n'est pas trouvé"""
        # Arrange
        mock_service_instance = Mock()
        mock_soundboard_service.return_value = mock_service_instance
        mock_service_instance.get_public_soundboard.return_value = None
        
        # Act
        result = self.service.generate_public(self.soundboard_uuid, self.playlist_uuid)
        
        # Assert
        self.assertIsNone(result)
        mock_service_instance.get_public_soundboard.assert_called_once_with(self.soundboard_uuid)

    @patch('main.service.RandomizeTrackService.SoundBoardService')
    @patch('main.service.RandomizeTrackService.MusicFilter')
    @patch('main.service.RandomizeTrackService.RandomizeTrackService._get_random_music_from_playlist')
    def test_generate_public_playlist_not_exist(self, mock_get_random, mock_music_filter, mock_soundboard_service):
        """Test génération aléatoire publique quand la playlist n'existe pas"""
        # Arrange
        mock_soundboard = Mock(spec=SoundBoard)
        mock_service_instance = Mock()
        mock_filter_instance = Mock()
        
        mock_soundboard_service.return_value = mock_service_instance
        mock_service_instance.get_public_soundboard.return_value = mock_soundboard
        mock_music_filter.return_value = mock_filter_instance
        mock_get_random.side_effect = Playlist.DoesNotExist()
        
        # Act
        result = self.service.generate_public(self.soundboard_uuid, self.playlist_uuid)
        
        # Assert
        self.assertIsNone(result)

    @patch('main.service.RandomizeTrackService.SoundBoardService')
    @patch('main.service.RandomizeTrackService.Track.objects')
    def test_get_shared_success(self, mock_track_objects, mock_soundboard_service):
        """Test récupération d'une track partagée avec succès"""
        # Arrange
        mock_soundboard = Mock(spec=SoundBoard)
        mock_track = Mock(spec=Track)
        mock_service_instance = Mock()
        
        mock_soundboard_service.return_value = mock_service_instance
        mock_service_instance.get_soundboard_from_shared_soundboard.return_value = mock_soundboard
        mock_track_objects.get.return_value = mock_track
        
        # Act
        result = self.service.get_shared(self.soundboard_uuid, self.playlist_uuid, self.token, self.music_id)
        
        # Assert
        self.assertEqual(result, mock_track)
        mock_service_instance.get_soundboard_from_shared_soundboard.assert_called_once_with(
            self.soundboard_uuid, self.token
        )
        mock_track_objects.get.assert_called_once_with(
            pk=self.music_id, playlist__uuid=self.playlist_uuid
        )

    @patch('main.service.RandomizeTrackService.SoundBoardService')
    def test_get_shared_soundboard_not_found(self, mock_soundboard_service):
        """Test récupération d'une track partagée quand le soundboard n'est pas trouvé"""
        # Arrange
        mock_service_instance = Mock()
        mock_soundboard_service.return_value = mock_service_instance
        mock_service_instance.get_soundboard_from_shared_soundboard.return_value = None
        
        # Act
        result = self.service.get_shared(self.soundboard_uuid, self.playlist_uuid, self.token, self.music_id)
        
        # Assert
        self.assertIsNone(result)
        mock_service_instance.get_soundboard_from_shared_soundboard.assert_called_once_with(
            self.soundboard_uuid, self.token
        )

    @patch('main.service.RandomizeTrackService.SoundBoardService')
    @patch('main.service.RandomizeTrackService.Track.objects')
    def test_get_shared_track_not_exist(self, mock_track_objects, mock_soundboard_service):
        """Test récupération d'une track partagée quand la track n'existe pas"""
        # Arrange
        mock_soundboard = Mock(spec=SoundBoard)
        mock_service_instance = Mock()
        
        mock_soundboard_service.return_value = mock_service_instance
        mock_service_instance.get_soundboard_from_shared_soundboard.return_value = mock_soundboard
        mock_track_objects.get.side_effect = Track.DoesNotExist()
        
        # Act
        result = self.service.get_shared(self.soundboard_uuid, self.playlist_uuid, self.token, self.music_id)
        
        # Assert
        self.assertIsNone(result)

    @patch('main.service.RandomizeTrackService.SoundBoardService')
    @patch('main.service.RandomizeTrackService.Track.objects')
    def test_get_shared_playlist_not_exist(self, mock_track_objects, mock_soundboard_service):
        """Test récupération d'une track partagée quand la playlist n'existe pas"""
        # Arrange
        mock_soundboard = Mock(spec=SoundBoard)
        mock_service_instance = Mock()
        
        mock_soundboard_service.return_value = mock_service_instance
        mock_service_instance.get_soundboard_from_shared_soundboard.return_value = mock_soundboard
        mock_track_objects.get.side_effect = Playlist.DoesNotExist()
        
        # Act
        result = self.service.get_shared(self.soundboard_uuid, self.playlist_uuid, self.token, self.music_id)
        
        # Assert
        self.assertIsNone(result)

    def test_get_random_music_from_playlist_success(self):
        """Test récupération aléatoire d'une musique depuis une playlist avec succès"""
        # Arrange
        mock_music = Mock(spec=Music)
        mock_filter = Mock(spec=MusicFilter)
        mock_queryset = Mock()
        mock_ordered_queryset = Mock()
        
        mock_filter.filter_by_playlist.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_ordered_queryset
        mock_ordered_queryset.first.return_value = mock_music
        
        # Act
        result = self.service._get_random_music_from_playlist(mock_filter, self.playlist_uuid)
        
        # Assert
        self.assertEqual(result, mock_music)
        mock_filter.filter_by_playlist.assert_called_once_with(self.playlist_uuid)
        mock_queryset.order_by.assert_called_once_with('?')
        mock_ordered_queryset.first.assert_called_once()

    def test_get_random_music_from_playlist_no_music(self):
        """Test récupération aléatoire d'une musique depuis une playlist vide"""
        # Arrange
        mock_filter = Mock(spec=MusicFilter)
        mock_queryset = Mock()
        mock_ordered_queryset = Mock()
        
        mock_filter.filter_by_playlist.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_ordered_queryset
        mock_ordered_queryset.first.return_value = None
        
        # Act
        result = self.service._get_random_music_from_playlist(mock_filter, self.playlist_uuid)
        
        # Assert
        self.assertIsNone(result)
        mock_filter.filter_by_playlist.assert_called_once_with(self.playlist_uuid)
        mock_queryset.order_by.assert_called_once_with('?')
        mock_ordered_queryset.first.assert_called_once()