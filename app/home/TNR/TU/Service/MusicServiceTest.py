from django.test import TestCase, RequestFactory
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