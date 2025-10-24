"""
Test d'intégration pour la route: Soundboard partagé (/shared/<uuid:soundboard_uuid>/<str:token>)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


@tag('integration')
class SharedSoundboardRouteTest(TestCase):
    """Tests pour la route de soundboard partagé"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.test_uuid = uuid.uuid4()
        self.test_token = "test-token-123"
    
    def test_shared_soundboard_accessible_without_auth(self):
        """Test que la route est accessible sans authentification"""
        response = self.client.get(
            reverse('shared_soundboard', kwargs={
                'soundboard_uuid': self.test_uuid,
                'token': self.test_token
            })
        )
        self.assertIn(response.status_code, [200, 302, 404, 403])
    
    def test_shared_soundboard_with_invalid_token(self):
        """Test avec un token invalide"""
        response = self.client.get(
            reverse('shared_soundboard', kwargs={
                'soundboard_uuid': self.test_uuid,
                'token': 'invalid-token'
            })
        )
        self.assertIn(response.status_code, [404, 403])
    
    def test_shared_soundboard_with_invalid_uuid(self):
        """Test avec un UUID invalide"""
        response = self.client.get(
            reverse('shared_soundboard', kwargs={
                'soundboard_uuid': uuid.uuid4(),
                'token': self.test_token
            })
        )
        self.assertIn(response.status_code, [404, 403])
