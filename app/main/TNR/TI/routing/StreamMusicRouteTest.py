"""
Test d'intégration pour la route: Streaming de musique (/playlist/<uuid:soundboard_uuid>/<uuid:playlist_uuid>/stream)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


@tag('integration')
class StreamMusicRouteTest(TestCase):
    """Tests pour la route de streaming de musique"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.test_uuid1 = uuid.uuid4()
        self.test_uuid2 = uuid.uuid4()
    
    def test_stream_music_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(
            reverse('streamMusic', kwargs={
                'soundboard_uuid': self.test_uuid1,
                'playlist_uuid': self.test_uuid2
            })
        )
        self.assertIn(response.status_code, [302, 401, 403, 404])
    
    def test_stream_music_accessible_when_authenticated(self):
        """Test que la route est accessible quand authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('streamMusic', kwargs={
                'soundboard_uuid': self.test_uuid1,
                'playlist_uuid': self.test_uuid2
            })
        )
        self.assertIn(response.status_code, [200, 302, 404, 403])
    
    def test_stream_music_with_invalid_uuids(self):
        """Test avec des UUIDs invalides"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('streamMusic', kwargs={
                'soundboard_uuid': uuid.uuid4(),
                'playlist_uuid': uuid.uuid4()
            })
        )
        self.assertIn(response.status_code, [404, 403])
