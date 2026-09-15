"""
Test d'intégration pour la route: mise à jour d'une playlist (/playlist/<uuid:playlist_uuid>/update)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistTag import PlaylistTag
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PlaylistUpdateRouteTest(TestCase):
    """Tests pour la route playlist_update (GET/POST)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        # Create test tags
        self.tag = PlaylistTag.objects.create(name='Action', label='action', is_active=True)

        self.playlist = Playlist.objects.create(
            user=self.user, name='Ma playlist', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.other_playlist = Playlist.objects.create(
            user=self.other_user, name='Playlist autre', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )

    def _url(self, playlist_uuid=None):
        return reverse('playlistUpdate', kwargs={'playlist_uuid': playlist_uuid or self.playlist.uuid})

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
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(playlist_uuid=self.other_playlist.uuid))
        self.assertEqual(response.status_code, 404)

    def test_post_updates_playlist_name(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(), {
            'name': 'Nouveau nom',
            'typePlaylist': PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            'color': '#000000',
            'colorText': '#ffffff',
            'volume': 100,
            'maxDelay': 0,
            'fadeIn': 'DEFAULT',
            'fadeOut': 'DEFAULT',
            'playlist_tags': [str(self.tag.pk)],
        })
        self.assertEqual(response.status_code, 302)
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.name, 'Nouveau nom')

    def test_post_with_invalid_data_redisplays_form(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(), {
            'name': '',
            'typePlaylist': PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            'playlist_tags': [str(self.tag.pk)],
        })
        self.assertEqual(response.status_code, 200)
