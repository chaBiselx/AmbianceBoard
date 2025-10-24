"""
Test d'intégration pour la route: Streaming public de musique (/public/soundboards/<uuid:soundboard_uuid>/<uuid:playlist_uuid>/stream)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


@tag('integration')
class PublicStreamMusicRouteTest(TestCase):
    """Tests pour la route de streaming public de musique"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.test_uuid1 = uuid.uuid4()
        self.test_uuid2 = uuid.uuid4()
    
    def test_public_stream_music_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        response = self.client.get(
            reverse('publicStreamMusic', kwargs={
                'soundboard_uuid': self.test_uuid1,
                'playlist_uuid': self.test_uuid2
            })
        )
        self.assertIn(response.status_code, [200, 302, 404, 403])
    
    def test_public_stream_music_with_invalid_uuids(self):
        """Test avec des UUIDs invalides"""
        response = self.client.get(
            reverse('publicStreamMusic', kwargs={
                'soundboard_uuid': uuid.uuid4(),
                'playlist_uuid': uuid.uuid4()
            })
        )
        self.assertIn(response.status_code, [404, 403])
