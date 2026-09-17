"""
Test d'intégration pour la route: updateShortcutPlaylistsForPlayers (UPDATE /soundBoards/specific/shortcut/update)
"""
import json

from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.SoundboardSection import SoundboardSection

User = get_user_model()


@tag('integration')
class UpdateShortcutPlaylistsForPlayersRouteTest(TestCase):
    """Tests pour la route updateShortcutPlaylistsForPlayers (UPDATE)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')
        self.playlist = Playlist.objects.create(user=self.user, name='Playlist')
        self.section = SoundboardSection.objects.create(
            SoundBoard=self.soundboard, section=1, name='Section 1', order=1
        )
        self.soundboard_playlist = SoundboardPlaylist.objects.create(
            Playlist=self.playlist, section=self.section, order=1, shortcut_keyboard=None
        )

    def _url(self):
        return reverse('updateShortcutPlaylistsForPlayers')

    def _payload(self, **overrides):
        payload = {
            'soundboard_uuid': str(self.soundboard.uuid),
            'playlist_uuid': str(self.playlist.uuid),
            'soundboard_playlist_id': self.soundboard_playlist.id,
            'shortcuts': ['a', 'b'],
        }
        payload.update(overrides)
        return payload

    def _update(self, payload):
        return self.client.generic(
            method='UPDATE',
            path=self._url(),
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_requires_authentication(self):
        response = self._update(self._payload())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_updates_shortcuts_for_owner(self):
        self.client.login(username='owner', password='pw')
        response = self._update(self._payload())
        self.assertEqual(response.status_code, 200)
        self.soundboard_playlist.refresh_from_db()
        self.assertEqual(self.soundboard_playlist.shortcut_keyboard, ['a', 'b'])

    def test_returns_400_when_soundboard_playlist_not_found(self):
        self.client.login(username='owner', password='pw')
        response = self._update(self._payload(soundboard_playlist_id=999999))
        self.assertEqual(response.status_code, 400)

    def test_returns_400_when_uuids_do_not_match(self):
        self.client.login(username='owner', password='pw')
        response = self._update(self._payload(
            soundboard_uuid='11111111-1111-1111-1111-111111111111',
            playlist_uuid='00000000-0000-0000-0000-000000000000',
        ))
        self.assertEqual(response.status_code, 400)
