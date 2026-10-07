"""
Test d'intégration pour la route: soundboardEditModePlaylistList (GET /soundBoards/<uuid>/edit-mode/playlist-list)
"""
from django.test import tag
from django.urls import reverse
from django.http import StreamingHttpResponse
from unittest.mock import patch

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Track import Track
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase
import uuid


@tag('integration')
class SoundboardEditModePlaylistListRouteTest(AuthenticatedTestCase):
    """Tests pour la route soundboardEditModePlaylistList (GET)."""

    def setUp(self):
        super().setUp()
        self.other_user = self.create_user(username='other')

        self.soundboard = self.create_soundboard(name='Board')

        self.copiable_playlist = self.create_playlist(
            user=self.other_user, name='Copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True, moderator_ban_copie=False
        )
        Track.objects.create(playlist=self.copiable_playlist, alternativeName='Track')

        self.not_copiable_playlist = self.create_playlist(
            user=self.other_user, name='Non copiable', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=False
        )
        Track.objects.create(playlist=self.not_copiable_playlist, alternativeName='Track')

    def _url(self, soundboard_uuid=None):
        return reverse('soundboardEditModePlaylistList', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid
        })

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_owner(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_404_for_nonexistent_soundboard(self):
        self.login()
        response = self.client.get(self._url(soundboard_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_response_contains_copiable_playlist(self):
        self.login()
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertIn(self.copiable_playlist.name, content)

    def test_response_excludes_non_copiable_playlist(self):
        self.login()
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertNotIn(self.not_copiable_playlist.name, content)

    def test_preview_lists_tracks_collapsed_without_audio_source(self):
        self.login()
        response = self.client.get(self._url())
        self.assertContains(response, 'class="collapse community-track-list"')
        self.assertContains(response, 'aria-expanded="false"')
        self.assertContains(response, '<div class="small text-break">Track</div>', html=True)
        self.assertContains(response, 'data-url="' + self._stream_url() + '"')
        self.assertContains(response, '<audio preload="none" class="music-player d-none"></audio>', html=True)

    def test_preview_tracks_are_preloaded_with_subtypes(self):
        from main.architecture.persistence.repository.PlaylistRepository import PlaylistRepository
        with self.assertNumQueries(2):
            playlists = list(PlaylistRepository().get_copiable_playlists_for_soundboard(self.user, {}))
            self.assertEqual(playlists[0].preview_tracks[0].get_name(), 'Track')

    def test_my_playlists_do_not_get_community_preview(self):
        self.login()
        playlist = self.create_playlist(name='My own playlist', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name)
        Track.objects.create(playlist=playlist, alternativeName='My own track')
        url = reverse('soundboardEditModeMyPlaylistList', kwargs={'soundboard_uuid': self.soundboard.uuid})
        response = self.client.get(url)
        self.assertContains(response, playlist.name)
        self.assertNotContains(response, 'community-track-list')
        self.assertNotContains(response, 'soundboardEditModeCommunityTrackStream')

    def test_type_filter_is_applied(self):
        self.login()
        response = self.client.get(self._url(), {'playlistType': PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.value})
        content = response.content.decode('utf-8')
        self.assertNotIn(self.copiable_playlist.name, content)

    def test_page_query_param_is_accepted(self):
        self.login()
        response = self.client.get(self._url(), {'page': 1})
        self.assertEqual(response.status_code, 200)

    def _stream_url(self, playlist=None, music_id=None, soundboard=None):
        playlist = playlist or self.copiable_playlist
        return reverse('soundboardEditModeCommunityTrackStream', kwargs={
            'soundboard_uuid': (soundboard or self.soundboard).uuid,
            'playlist_uuid': playlist.uuid,
            'music_id': music_id or playlist.tracks.first().id,
        })

    def test_preview_stream_requires_current_authentication(self):
        for method in (self.client.get, self.client.head):
            self.assertEqual(method(self._stream_url()).status_code, 302)
        self.login()
        self.client.logout()
        self.assertEqual(self.client.get(self._stream_url()).status_code, 302)

    @patch.object(Track, 'get_reponse_content')
    def test_preview_stream_returns_audio_for_authenticated_owner(self, mock_content):
        self.login()
        mock_content.return_value = StreamingHttpResponse([b'audio'], content_type='audio/mpeg')
        response = self.client.get(self._stream_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b''.join(response.streaming_content), b'audio')
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        mock_content.assert_called_once()

    @patch.object(Track, 'get_reponse_content')
    def test_preview_head_does_not_load_audio(self, mock_content):
        self.login()
        response = self.client.head(self._stream_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        mock_content.assert_not_called()

    @patch.object(Track, 'get_reponse_content')
    def test_preview_rejects_private_banned_and_foreign_tracks(self, mock_content):
        self.login()
        self.assertEqual(self.client.get(self._stream_url(self.not_copiable_playlist)).status_code, 404)
        foreign_track = self.not_copiable_playlist.tracks.first()
        self.assertEqual(self.client.get(self._stream_url(music_id=foreign_track.id)).status_code, 404)
        self.copiable_playlist.moderator_ban_copie = True
        self.copiable_playlist.save()
        for method in (self.client.get, self.client.head):
            self.assertEqual(method(self._stream_url()).status_code, 404)
        mock_content.assert_not_called()

    @patch.object(Track, 'get_reponse_content')
    def test_preview_rejects_other_users_soundboard_and_missing_resources(self, mock_content):
        self.login()
        other_board = self.create_soundboard(user=self.other_user)
        self.assertEqual(self.client.get(self._stream_url(soundboard=other_board)).status_code, 404)
        self.assertEqual(self.client.get(self._stream_url(music_id=999999)).status_code, 404)
        url = self._stream_url()
        self.copiable_playlist.delete()
        self.assertEqual(self.client.get(url).status_code, 404)
        mock_content.assert_not_called()

    @patch.object(Track, 'get_reponse_content', side_effect=ValueError('Unavailable'))
    def test_preview_handles_unavailable_audio(self, mock_content):
        self.login()
        self.assertEqual(self.client.get(self._stream_url()).status_code, 404)

    def test_preview_rejects_post(self):
        self.login()
        self.assertEqual(self.client.post(self._stream_url()).status_code, 405)
