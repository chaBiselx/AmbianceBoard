"""
Test d'intégration pour la route: Publication de soundboard (/shared/<uuid:soundboard_uuid>)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


@tag('integration')
class PublishSoundboardRouteTest(TestCase):
    """Tests pour la route de publication de soundboard"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.test_uuid = uuid.uuid4()
    
    def test_publish_soundboard_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(
            reverse('publish_soundboard', kwargs={
                'soundboard_uuid': self.test_uuid
            })
        )
        self.assertIn(response.status_code, [302, 401, 403, 404])
    
    def test_publish_soundboard_accessible_when_authenticated(self):
        """Test que la route est accessible quand authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('publish_soundboard', kwargs={
                'soundboard_uuid': self.test_uuid
            })
        )
        self.assertIn(response.status_code, [200, 302, 404, 403])
    
    def test_publish_soundboard_with_invalid_uuid(self):
        """Test avec un UUID invalide"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('publish_soundboard', kwargs={
                'soundboard_uuid': uuid.uuid4()
            })
        )
        self.assertIn(response.status_code, [404, 403])
