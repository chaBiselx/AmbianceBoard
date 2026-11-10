from unittest.mock import patch

from django.test import TestCase, tag
from django.urls import reverse

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.models.TrackLabel import TrackLabel
from main.architecture.persistence.models.User import User
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


@tag('integration')
class TrackLabelReportRouteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='label_reporter', email='reporter@example.com', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other_label_owner', email='other@example.com', password='testpass123'
        )
        self.playlist = Playlist.objects.create(
            user=self.user,
            name='Forest playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        self.track = Track.objects.create(playlist=self.playlist, alternativeName='Forest rain')
        self.label = TrackLabel.objects.create(
            track=self.track, category='environment', label='rain', confidence=0.82
        )
        self.other_track = Track.objects.create(playlist=self.playlist, alternativeName='Wind')
        self.other_label = TrackLabel.objects.create(
            track=self.other_track, category='environment', label='wind', confidence=0.7
        )
        self.url = reverse('reportTrackLabels', kwargs={
            'playlist_uuid': self.playlist.uuid,
            'track_id': self.track.id,
        })
        self.client.force_login(self.user)

    def test_requires_authentication(self):
        self.client.logout()
        response = self.client.post(self.url, {'label_ids': str(self.label.id)})
        self.assertEqual(response.status_code, 302)

    def test_sends_report_for_selected_label(self):
        with patch('main.interface.ui.controller.private.playlistFormTrackViews.TrackLabelReportEmail.send_report') as send_report:
            response = self.client.post(self.url, {'label_ids': str(self.label.id)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True})
        args = send_report.call_args.args
        self.assertEqual(args[0], self.track)
        self.assertEqual(list(args[1]), [self.label])
        self.assertEqual(args[2], self.user)

    def test_rejects_empty_or_unrelated_label_ids(self):
        empty_response = self.client.post(self.url, {})
        unrelated_response = self.client.post(self.url, {'label_ids': str(self.other_label.id)})

        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(unrelated_response.status_code, 400)

    def test_rejects_playlist_owned_by_another_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.url, {'label_ids': str(self.label.id)})

        self.assertEqual(response.status_code, 404)

    def test_returns_server_error_when_email_is_not_sent(self):
        with patch(
            'main.interface.ui.controller.private.playlistFormTrackViews.TrackLabelReportEmail.send_report',
            return_value=False,
        ):
            response = self.client.post(self.url, {'label_ids': str(self.label.id)})

        self.assertEqual(response.status_code, 500)