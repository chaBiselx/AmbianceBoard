"""
Test d'intégration pour la route: add_music_from_soundboard (GET /soundBoards/add-music/<uuid>)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.architecture.persistence.models.Playlist import Playlist
import uuid

User = get_user_model()


@tag('integration')
class AddMusicFromSoundboardRouteTest(TestCase):
    """Tests pour la route add_music_from_soundboard (GET)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.playlist = Playlist.objects.create(user=self.user, name='Playlist')

    def _url(self, playlist_uuid=None):
        return reverse('add_music_from_soundboard', kwargs={
            'playlist_uuid': playlist_uuid or self.playlist.uuid
        })

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_owner(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_nonexistent_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_playlist(self):
        self.client.login(username='other', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_clears_new_playlist_uuid_from_session(self):
        self.client.login(username='owner', password='pw')
        session = self.client.session
        session['new_playlist_uuid'] = str(self.playlist.uuid)
        session.save()
        self.client.get(self._url())
        self.assertNotIn('new_playlist_uuid', self.client.session)
