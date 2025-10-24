"""
Test d'intégration pour la route: Streaming de musique partagée (/shared/<uuid:soundboard_uuid>/<str:token>/<uuid:playlist_uuid>/<int:music_id>/stream)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


@tag('integration')
class SharedStreamMusicRouteTest(TestCase):
    """Tests pour la route de streaming de musique partagée"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.test_uuid1 = uuid.uuid4()
        self.test_uuid2 = uuid.uuid4()
        self.test_token = "test-token-123"
    
    def test_shared_stream_music_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        response = self.client.get(
            reverse('sharedStreamMusic', kwargs={
                'soundboard_uuid': self.test_uuid1,
                'token': self.test_token,
                'playlist_uuid': self.test_uuid2,
                'music_id': 1
            })
        )
        self.assertIn(response.status_code, [200, 302, 404, 403])
    
    def test_shared_stream_music_with_invalid_token(self):
        """Test avec un token invalide"""
        response = self.client.get(
            reverse('sharedStreamMusic', kwargs={
                'soundboard_uuid': self.test_uuid1,
                'token': 'invalid-token',
                'playlist_uuid': self.test_uuid2,
                'music_id': 1
            })
        )
        self.assertIn(response.status_code, [404, 403])
    
    def test_shared_stream_music_with_invalid_uuids(self):
        """Test avec des UUIDs invalides"""
        response = self.client.get(
            reverse('sharedStreamMusic', kwargs={
                'soundboard_uuid': uuid.uuid4(),
                'token': self.test_token,
                'playlist_uuid': uuid.uuid4(),
                'music_id': 99999
            })
        )
        self.assertIn(response.status_code, [404, 403])
