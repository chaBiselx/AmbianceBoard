"""
Test d'intégration pour la route: add_music_from_soundboard (GET /soundBoards/add-music/<uuid>)
"""
from django.test import tag
from django.urls import reverse
import uuid

from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class AddMusicFromSoundboardRouteTest(AuthenticatedTestCase):
    """Tests pour la route add_music_from_soundboard (GET)."""

    def setUp(self):
        super().setUp()
        self.other_user = self.create_user(username='other')

        self.playlist = self.create_playlist(name='Playlist')

    def _url(self, playlist_uuid=None):
        return reverse('add_music_from_soundboard', kwargs={
            'playlist_uuid': playlist_uuid or self.playlist.uuid
        })

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_owner(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_nonexistent_playlist(self):
        self.login()
        response = self.client.get(self._url(playlist_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_playlist(self):
        self.login(self.other_user)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_clears_new_playlist_uuid_from_session(self):
        self.login()
        session = self.client.session
        session['new_playlist_uuid'] = str(self.playlist.uuid)
        session.save()
        self.client.get(self._url())
        self.assertNotIn('new_playlist_uuid', self.client.session)
