from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from main.service.MusicService import MusicService
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User

class MusicServiceTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = self._create_user('test')
        self.other_user = self._create_user('otherName')
        
        self.playlist = self._create_playlist(1, self.user)
        self.other_playlist = self._create_playlist(2, self.other_user)
        
        self.music = self._create_test_music(self.playlist)
        self.other_music = self._create_test_music(self.other_playlist)

    def _create_user(self, username):
        return User.objects.create_user(
            username=username, 
            password='test' # NOSONAR
        )
    
    def _create_playlist(self, uuid, user):
        return Playlist.objects.create(
            uuid=uuid,
            name="test",
            user=user
        )
    
    def _create_test_music(self, playlist):
        return [
            Music.objects.create(
                fileName=f"File{i}",
                alternativeName="test",
                file=f"{filename}.mp3",
                playlist=playlist
            )
            for i, filename in enumerate(["AZERTY", "QWERTY", "123456"], 1)
        ]

    def _create_test_file(self, name="test.mp3", content=b'test content', size_mb=1):
        """Crée un fichier de test avec une taille spécifique"""
        content = b'x' * (size_mb * 1024 * 1024) if size_mb > 0 else content
        return SimpleUploadedFile(
            name=name,
            content=content,
            content_type='audio/mp3'
        )

    # Tests pour save_multiple_files_item
    @patch('main.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_success(self, mock_user_params_factory):
        """Test la sauvegarde réussie d'un fichier multiple"""
        # Configuration du mock pour les paramètres utilisateur
        mock_user_params = MagicMock()
        mock_user_params.limit_music_per_playlist = 10
        mock_user_params.limit_weight_file = 5  # 5 Mo
        mock_user_params_factory.return_value = mock_user_params

        request = self.factory.post('/')
        request.user = self.user
        
        music_service = MusicService(request)
        
        # Créer un nouveau playlist pour éviter les conflits avec les musiques existantes
        new_playlist = Playlist.objects.create(
            uuid=999,
            name="test_multiple",
            user=self.user
        )
        
        test_file = self._create_test_file("new_song.mp3", size_mb=2)
        
        # Exécuter la méthode
        music = music_service.save_multiple_files_item(new_playlist, test_file)
        
        # Vérifications
        self.assertIsNotNone(music)
        self.assertIsInstance(music, Music)
        self.assertEqual(music.alternativeName, 'new_song')
        self.assertEqual(music.playlist, new_playlist)
        self.assertTrue(music.file.name.endswith('.mp3'))

    @patch('main.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_limit_playlist_exceeded(self, mock_user_params_factory):
        """Test l'erreur quand la limite de musiques par playlist est dépassée"""
        # Configuration du mock pour une limite basse
        mock_user_params = MagicMock()
        mock_user_params.limit_music_per_playlist = 2  # Limite basse
        mock_user_params.limit_weight_file = 5
        mock_user_params_factory.return_value = mock_user_params

        request = self.factory.post('/')
        request.user = self.user
        
        music_service = MusicService(request)
        
        test_file = self._create_test_file("new_song.mp3")
        
        # Le playlist self.playlist a déjà 3 musiques, la limite est 2
        with self.assertRaises(ValueError) as context:
            music_service.save_multiple_files_item(self.playlist, test_file)
        
        self.assertIn("limite de musique par playlist", str(context.exception))

    @patch('main.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_file_too_large(self, mock_user_params_factory):
        """Test l'erreur quand le fichier est trop volumineux"""
        # Configuration du mock pour une limite de poids basse
        mock_user_params = MagicMock()
        mock_user_params.limit_music_per_playlist = 10
        mock_user_params.limit_weight_file = 1  # 1 Mo seulement
        mock_user_params_factory.return_value = mock_user_params

        request = self.factory.post('/')
        request.user = self.user
        
        music_service = MusicService(request)
        
        # Créer un nouveau playlist
        new_playlist = Playlist.objects.create(
            uuid=998,
            name="test_weight",
            user=self.user
        )
        
        # Créer un fichier de 2 Mo (dépasse la limite de 1 Mo)
        test_file = self._create_test_file("large_song.mp3", size_mb=2)
        
        with self.assertRaises(ValueError) as context:
            music_service.save_multiple_files_item(new_playlist, test_file)
        
        self.assertIn("poids du fichier est trop lourd", str(context.exception))

    @patch('main.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_invalid_extension(self, mock_user_params_factory):
        """Test l'erreur avec une extension de fichier non autorisée"""
        # Configuration du mock
        mock_user_params = MagicMock()
        mock_user_params.limit_music_per_playlist = 10
        mock_user_params.limit_weight_file = 5
        mock_user_params_factory.return_value = mock_user_params

        request = self.factory.post('/')
        request.user = self.user
        
        music_service = MusicService(request)
        
        # Créer un nouveau playlist
        new_playlist = Playlist.objects.create(
            uuid=997,
            name="test_extension",
            user=self.user
        )
        
        # Créer un fichier avec une extension non autorisée
        test_file = SimpleUploadedFile(
            name="invalid_file.txt",
            content=b'not an audio file',
            content_type='text/plain'
        )
        
        with self.assertRaises(ValueError) as context:
            music_service.save_multiple_files_item(new_playlist, test_file)
        
        self.assertIn("fichiers audio", str(context.exception))

    @patch('main.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_default_alternative_name(self, mock_user_params_factory):
        """Test que le nom alternatif par défaut est correctement généré"""
        # Configuration du mock
        mock_user_params = MagicMock()
        mock_user_params.limit_music_per_playlist = 10
        mock_user_params.limit_weight_file = 5
        mock_user_params_factory.return_value = mock_user_params

        request = self.factory.post('/')
        request.user = self.user
        
        music_service = MusicService(request)
        
        # Créer un nouveau playlist
        new_playlist = Playlist.objects.create(
            uuid=996,
            name="test_default_name",
            user=self.user
        )
        
        test_file = self._create_test_file("my_awesome_song.mp3")
        
        music = music_service.save_multiple_files_item(new_playlist, test_file)
        
        # Le nom alternatif devrait être le nom du fichier sans extension
        self.assertEqual(music.alternativeName, 'my_awesome_song')

    @patch('main.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_truncate_long_name(self, mock_user_params_factory):
        """Test que le nom de fichier long est tronqué à 63 caractères pour alternativeName"""
        # Configuration du mock
        mock_user_params = MagicMock()
        mock_user_params.limit_music_per_playlist = 10
        mock_user_params.limit_weight_file = 5
        mock_user_params_factory.return_value = mock_user_params

        request = self.factory.post('/')
        request.user = self.user
        
        music_service = MusicService(request)
        
        # Créer un nouveau playlist
        new_playlist = Playlist.objects.create(
            uuid=995,
            name="test_truncate",
            user=self.user
        )
        
        # Nom très long (plus de 63 caractères)
        long_name = "a" * 70
        test_file = self._create_test_file(f"{long_name}.mp3")

        music = music_service.save_multiple_files_item(new_playlist, test_file)
        
        # Le nom devrait être tronqué à 63 caractères
        self.assertEqual(len(music.alternativeName), 63)
        self.assertEqual(music.alternativeName, long_name[:63])

    @patch('main.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_various_audio_formats(self, mock_user_params_factory):
        """Test avec différents formats audio autorisés"""
        # Configuration du mock
        mock_user_params = MagicMock()
        mock_user_params.limit_music_per_playlist = 10
        mock_user_params.limit_weight_file = 5
        mock_user_params_factory.return_value = mock_user_params

        request = self.factory.post('/')
        request.user = self.user
        
        music_service = MusicService(request)
        
        # Tester différents formats
        formats = ['.mp3', '.wav', '.ogg']
        
        for i, format_ext in enumerate(formats):
            with self.subTest(format=format_ext):
                # Créer un nouveau playlist pour chaque test
                playlist = Playlist.objects.create(
                    uuid=990 + i,
                    name=f"test_format_{format_ext}",
                    user=self.user
                )
                
                test_file = SimpleUploadedFile(
                    name=f"test_song{format_ext}",
                    content=b'audio content',
                    content_type=f'audio/{format_ext[1:]}'
                )
                
                # Ne devrait pas lever d'exception
                music = music_service.save_multiple_files_item(playlist, test_file)
                self.assertIsNotNone(music)
                self.assertTrue(music.file.name.endswith(format_ext))

    def tearDown(self):
        """Nettoyage après les tests"""
        # Supprimer les fichiers créés pendant les tests
        for music in Music.objects.all():
            if music.file:
                storage = music.file.storage
                if storage.exists(music.file.name):
                    storage.delete(music.file.name)
        Track.objects.all().delete()