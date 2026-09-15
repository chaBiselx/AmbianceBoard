"""
Test d'intégration pour la route: liste des playlists copiables (/playlist/public/copiable/all)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Track import Track
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PlaylistsAllCopiableListRouteTest(TestCase):
    """Tests pour la route playlist_read_copiable (GET)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.copiable_playlist = Playlist.objects.create(
            user=self.other_user, name='Playlist copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        Track.objects.create(playlist=self.copiable_playlist, alternativeName='Track')

        self.non_copiable_playlist = Playlist.objects.create(
            user=self.other_user, name='Playlist non copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=False,
        )
        Track.objects.create(playlist=self.non_copiable_playlist, alternativeName='Track')

        self.own_copiable_playlist = Playlist.objects.create(
            user=self.user, name='Ma propre playlist copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        Track.objects.create(playlist=self.own_copiable_playlist, alternativeName='Track')

        self.empty_copiable_playlist = Playlist.objects.create(
            user=self.other_user, name='Playlist copiable vide', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name,
            is_copiable=True,
        )

    def _url(self):
        return reverse('playlistsAllCopiableList')

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_authenticated_user(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_contains_other_users_copiable_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertIn(self.copiable_playlist.name, content)

    def test_excludes_non_copiable_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertNotIn(self.non_copiable_playlist.name, content)

    def test_excludes_own_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertNotIn(self.own_copiable_playlist.name, content)

    def test_excludes_empty_playlist(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertNotIn(self.empty_copiable_playlist.name, content)

    def test_type_filter_is_applied(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(), {'playlistType': PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.value})
        content = response.content.decode('utf-8')
        self.assertIn(self.copiable_playlist.name, content)
