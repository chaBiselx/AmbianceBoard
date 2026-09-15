"""
Test d'intégration pour la route: Rafraîchissement d'un soundboard partagé
(/shared/<uuid:soundboard_uuid>/<str:token>/refresh)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SharedSoundboard import SharedSoundboard

User = get_user_model()


@tag('integration')
class SharedSoundboardRefreshRouteTest(TestCase):
    """Tests pour la route de rafraîchissement d'un soundboard partagé"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='shared_refresh_owner', email='shared_refresh_owner@test.com', password='Test1234!')
        self.soundboard = SoundBoard.objects.create(user=self.user, name='SB Shared Refresh')
        self.shared = SharedSoundboard.objects.create(soundboard=self.soundboard)

    def test_shared_refresh_accessible_without_auth(self):
        """Test que la route est accessible sans authentification avec un token valide"""
        response = self.client.get(
            reverse('shared_soundboard_refresh', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'token': self.shared.token,
            })
        )
        self.assertEqual(response.status_code, 200)

    def test_shared_refresh_with_invalid_token(self):
        """Test avec un token invalide"""
        response = self.client.get(
            reverse('shared_soundboard_refresh', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'token': 'invalid-token',
            })
        )
        self.assertEqual(response.status_code, 404)

    def test_shared_refresh_with_invalid_uuid(self):
        """Test avec un UUID de soundboard inexistant"""
        response = self.client.get(
            reverse('shared_soundboard_refresh', kwargs={
                'soundboard_uuid': uuid.uuid4(),
                'token': str(self.shared.token),
            })
        )
        self.assertEqual(response.status_code, 404)
