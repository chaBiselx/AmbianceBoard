"""
Test d'intégration pour la route: updateActionablePlaylistsForPlayers (UPDATE /soundBoards/specific/actionnable/update)
"""
import json

from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.UserTier import UserTier

User = get_user_model()


@tag('integration')
class UpdateActionablePlaylistsForPlayersRouteTest(TestCase):
    """Tests pour la route updateActionablePlaylistsForPlayers (UPDATE)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        UserTier.objects.create(user=self.user, tier_name='PREMIUM_BASIC')

        self.standard_user = User.objects.create_user(username='standard', email='standard@test.com', password='pw')  # NOSONAR
        UserTier.objects.create(user=self.standard_user, tier_name='STANDARD')

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')
        self.playlist = Playlist.objects.create(user=self.user, name='Playlist')
        self.soundboard_playlist = SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard, Playlist=self.playlist, section=1, order=1, activable_by_player=False
        )

    def _url(self):
        return reverse('updateActionablePlaylistsForPlayers')

    def _payload(self, **overrides):
        payload = {
            'soundboard_uuid': str(self.soundboard.uuid),
            'playlist_uuid': str(self.playlist.uuid),
            'soundboard_playlist_id': self.soundboard_playlist.id,
            'label': 'playable_by_players',
            'value': True,
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

    def test_returns_403_when_user_lacks_permission(self):
        self.client.login(username='standard', password='pw')
        response = self._update(self._payload())
        self.assertEqual(response.status_code, 403)

    def test_updates_playlist_for_user_with_permission(self):
        self.client.login(username='owner', password='pw')
        response = self._update(self._payload())
        self.assertEqual(response.status_code, 200)
        self.soundboard_playlist.refresh_from_db()
        self.assertTrue(self.soundboard_playlist.activable_by_player)

    def test_returns_400_when_soundboard_playlist_not_found(self):
        self.client.login(username='owner', password='pw')
        response = self._update(self._payload(soundboard_playlist_id=999999))
        self.assertEqual(response.status_code, 400)

    def test_returns_400_when_uuids_do_not_match(self):
        self.client.login(username='owner', password='pw')
        response = self._update(self._payload(
            playlist_uuid='00000000-0000-0000-0000-000000000000',
            soundboard_uuid='11111111-1111-1111-1111-111111111111',
        ))
        self.assertEqual(response.status_code, 400)
