"""
Test d'intégration pour la route: publicFavoriteSoundboard (POST/DELETE /soundBoards/<uuid>/user/favorite)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.UserFavoritePublicSoundboard import UserFavoritePublicSoundboard
import uuid

User = get_user_model()


@tag('integration')
class PublicFavoriteSoundboardRouteTest(TestCase):
    """Tests pour la route publicFavoriteSoundboard (POST/DELETE)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.other_user, name='Board', is_public=True)

    def _url(self, soundboard_uuid=None):
        return reverse('publicFavoriteSoundboard', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid
        })

    def test_requires_authentication(self):
        response = self.client.post(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_post_adds_favorite(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['message'], 'success')
        self.assertTrue(
            UserFavoritePublicSoundboard.objects.filter(user=self.user, uuidSoundboard=self.soundboard).exists()
        )

    def test_post_returns_404_for_nonexistent_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(soundboard_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_delete_removes_favorite(self):
        self.client.login(username='owner', password='pw')
        UserFavoritePublicSoundboard.objects.create(user=self.user, uuidSoundboard=self.soundboard)
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['message'], 'success')
        self.assertFalse(
            UserFavoritePublicSoundboard.objects.filter(user=self.user, uuidSoundboard=self.soundboard).exists()
        )

    def test_delete_returns_404_when_favorite_not_found(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, 404)

    def test_returns_405_on_get_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
