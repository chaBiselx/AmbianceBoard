from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from home.service.MusicService import MusicService
from home.models.Music import Music
from home.models.Playlist import Playlist
from home.models.User import User

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
            password='test'
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
    
    # Test get_random_music
    def test_get_random_music(self):
        request = self.factory.get('/')
        request.user = self.user
        
        music_service = MusicService(request)
        music = music_service.get_random_music(1)
        self.assertEqual(music.alternativeName, "test")
    
    def test_get_random_music_random(self):
        request = self.factory.get('/')
        request.user = self.user
        
        music_service = MusicService(request)
        results = []
        for _ in range(50):  # Faire 50 appels
            random_music = music_service.get_random_music(1)
            results.append(random_music)
        
        unique_results = set(results)
        self.assertGreater(
            len(unique_results), 
            1,
            "La fonction ne semble pas retourner des résultats aléatoires"
        )
        
        self.assertGreater(
            len(unique_results),
            len(self.music) * 0.33,
            "La distribution des résultats aléatoires semble trop uniforme"
        )
    
    def test_get_random_music_incorrect_playlist(self):
        request = self.factory.get('/')
        request.user = self.user
        
        music_service = MusicService(request)
        music = music_service.get_random_music(9999)
        self.assertEqual(music, None)
        
    def test_get_random_music_other_user(self):
        request = self.factory.get('/')
        request.user = self.user
        
        music_service = MusicService(request)
        music = music_service.get_random_music(2)
        self.assertEqual(music, None)
        
    # Test get_list_music
    def test_get_list_music(self):
        request = self.factory.get('/')
        request.user = self.user
        
        music_service = MusicService(request)
        music = music_service.get_list_music(1)
        self.assertTrue(music.exists())
        self.assertEqual(len(music), 3) 
        
    def test_get_list_music_incorrect_playlist(self):
        request = self.factory.get('/')
        request.user = self.user
        
        music_service = MusicService(request)
        music = music_service.get_list_music(9999)
        self.assertFalse(music.exists())
        
    def test_get_list_music_other_user(self):
        request = self.factory.get('/')
        request.user = self.user
        
        music_service = MusicService(request)
        music = music_service.get_list_music(2)
        self.assertFalse(music.exists())

    # Tests pour save_multiple_files_item
    @patch('home.service.MusicService.UserParametersFactory')
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
        file_data = {
            'file': test_file,
            'alternativeName': 'Test Song 1'
        }
        
        # Exécuter la méthode
        music = music_service.save_multiple_files_item(new_playlist, file_data)
        
        # Vérifications
        self.assertIsNotNone(music)
        self.assertIsInstance(music, Music)
        self.assertEqual(music.alternativeName, 'Test Song 1')
        self.assertEqual(music.playlist, new_playlist)
        self.assertTrue(music.file.name.endswith('.mp3'))

    @patch('home.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_limit_playlist_exceeded(self, mock_user_params_factory):
        """Test l'erreur quand la limite de musiques par playlist est dépassée"""
        # Configuration du mock pour une limite basse
        mock_user_params = MagicMock()
        mock_user_params.limit_music_per_playlist = 2  # Limite basse
        mock_user_params.limit_weight_file = 5
        mock_user_params_factory.return_value = mock_user_params

        request = self.factory.post('/')
        request.user = self.user
        
        self.playlist.musics.add(self.music[0], self.music[1])  # Ajout de 2 musiques
        self.playlist.save()  # Sauvegarder la playlist avec les musiques
        
        music_service = MusicService(request)
        
        test_file = self._create_test_file("new_song.mp3")
        file_data = {
            'file': test_file,
            'alternativeName': 'Exceeded Song'
        }
        
        # Le playlist self.playlist a déjà 3 musiques, limite est 2
        with self.assertRaises(ValueError) as context:
            music_service.save_multiple_files_item(self.playlist, file_data)
        
        self.assertIn("limite de musique par playlist", str(context.exception))

    @patch('home.service.MusicService.UserParametersFactory')
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
        file_data = {
            'file': test_file,
            'alternativeName': 'Large Song'
        }
        
        with self.assertRaises(ValueError) as context:
            music_service.save_multiple_files_item(new_playlist, file_data)
        
        self.assertIn("poids du fichier est trop lourd", str(context.exception))

    @patch('home.service.MusicService.UserParametersFactory')
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
        file_data = {
            'file': test_file,
            'alternativeName': 'Invalid File'
        }
        
        with self.assertRaises(ValueError) as context:
            music_service.save_multiple_files_item(new_playlist, file_data)
        
        self.assertIn("fichiers audio", str(context.exception))

    @patch('home.service.MusicService.UserParametersFactory')
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
        file_data = {
            'file': test_file
            # Pas d'alternativeName fourni
        }
        
        music = music_service.save_multiple_files_item(new_playlist, file_data)
        
        # Le nom alternatif devrait être le nom du fichier sans extension
        self.assertEqual(music.alternativeName, 'my_awesome_song')

    @patch('home.service.MusicService.UserParametersFactory')
    def test_save_multiple_files_item_truncate_long_name(self, mock_user_params_factory):
        """Test que le nom alternatif long est tronqué à 63 caractères"""
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
        
        test_file = self._create_test_file("song.mp3")
        # Nom très long (plus de 63 caractères)
        long_name = "a" * 70
        file_data = {
            'file': test_file,
            'alternativeName': long_name
        }
        
        music = music_service.save_multiple_files_item(new_playlist, file_data)
        
        # Le nom devrait être tronqué à 63 caractères
        self.assertEqual(len(music.alternativeName), 63)
        self.assertEqual(music.alternativeName, long_name[:63])

    @patch('home.service.MusicService.UserParametersFactory')
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
                file_data = {
                    'file': test_file,
                    'alternativeName': f'Test format Song {format_ext}'
                }
                
                # Ne devrait pas lever d'exception
                music = music_service.save_multiple_files_item(playlist, file_data)
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