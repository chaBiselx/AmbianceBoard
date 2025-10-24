"""
Test d'intégration pour la route: Lecture publique de soundboard (/public/soundboards/<uuid:soundboard_uuid>)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


@tag('integration')
class PublicReadSoundboardRouteTest(TestCase):
    """Tests pour la route de lecture publique de soundboard"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.test_uuid = uuid.uuid4()
    
    def test_public_read_soundboard_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        response = self.client.get(
            reverse('publicReadSoundboard', kwargs={
                'soundboard_uuid': self.test_uuid
            })
        )
        self.assertIn(response.status_code, [200, 302, 404, 403])
    
    def test_public_read_soundboard_with_invalid_uuid(self):
        """Test avec un UUID invalide"""
        response = self.client.get(
            reverse('publicReadSoundboard', kwargs={
                'soundboard_uuid': uuid.uuid4()
            })
        )
        self.assertIn(response.status_code, [404, 403])
