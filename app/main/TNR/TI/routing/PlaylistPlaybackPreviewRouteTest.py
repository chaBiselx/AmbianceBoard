from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase, tag
from django.urls import reverse
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Track import Track


@tag('integration')
class PlaylistPlaybackPreviewRouteTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='preview-owner', password='testpass123')
        self.other = get_user_model().objects.create_user(username='preview-other', password='testpass123')
        self.playlist = Playlist.objects.create(user=self.user, name='Saved playlist', typePlaylist='PLAYLIST_TYPE_MUSIC')
        self.track = Track.objects.create(playlist=self.playlist, alternativeName='Current track', duration=120)
        self.modal_url = reverse('playlistPreviewModal', args=[self.playlist.uuid])
        self.stream_url = reverse('playlistPreviewStream', args=[self.playlist.uuid]) + '?i=preview-test'
        self.client.force_login(self.user)

    def test_modal_renders_saved_playlist_and_stream_configuration(self):
        response = self.client.get(self.modal_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Saved playlist')
        self.assertContains(response, 'data-playlist-preview="true"')
        self.assertContains(response, reverse('playlistPreviewStream', args=[self.playlist.uuid]))

    def test_requires_authentication_and_ownership(self):
        self.client.logout()
        for url in (self.modal_url, self.stream_url):
            self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.other)
        for url in (self.modal_url, self.stream_url):
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.get(url, HTTP_X_METADATA_ONLY='true').status_code, 404)

    def test_empty_playlist_and_invalid_method_are_rejected(self):
        self.track.delete()
        self.assertEqual(self.client.get(self.modal_url).status_code, 404)
        self.assertEqual(self.client.get(self.stream_url).status_code, 404)
        self.assertEqual(self.client.post(self.modal_url).status_code, 405)
        self.assertEqual(self.client.post(self.stream_url).status_code, 405)

    @patch.object(Track, 'get_reponse_content', return_value=HttpResponse(b'audio', content_type='audio/test'))
    def test_metadata_matches_the_streamed_track_without_another_random_draw(self, stream):
        response = self.client.get(self.stream_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'audio')
        self.assertIn('no-store', response['Cache-Control'])
        Track.objects.create(playlist=self.playlist, alternativeName='Other track', duration=10)
        with patch('main.domain.common.service.PlaylistPreviewService.RandomizeTrackService') as randomize:
            metadata = self.client.get(self.stream_url, HTTP_X_METADATA_ONLY='true')
            self.assertEqual(metadata.json(), {'track_id': self.track.id, 'name': 'Current track', 'duration': 120})
            randomize.assert_not_called()
        self.client.get(self.stream_url)
        self.assertEqual(stream.call_count, 2)

    def test_metadata_missing_or_from_another_playback_is_not_randomized(self):
        self.assertEqual(self.client.get(self.stream_url, HTTP_X_METADATA_ONLY='true').status_code, 404)
        self.assertEqual(self.client.get(self.stream_url + '-other', HTTP_X_METADATA_ONLY='true').status_code, 404)
        self.assertEqual(self.client.get(reverse('playlistPreviewStream', args=[self.playlist.uuid])).status_code, 404)