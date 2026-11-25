from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import SimpleTestCase, tag

from main.architecture.persistence.models.LinkMusic import LinkMusic
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Track import Track
from main.domain.common.strategy.urlMusicStream.FileStreamExtract import FileStreamExtract


@tag('unitaire')
class TrackModelTest(SimpleTestCase):
    def setUp(self):
        self.track = Track()
        self.track.music = Music(
            file=SimpleUploadedFile('song.mp3', b'0123456789', content_type='audio/mpeg'),
            fileName='song.mp3',
        )

    def test_local_track_returns_requested_byte_range(self):
        response = self.track.get_reponse_content('bytes=2-5')

        self.assertEqual(response.status_code, 206)
        self.assertEqual(response['Accept-Ranges'], 'bytes')
        self.assertEqual(response['Content-Length'], '4')
        self.assertEqual(response['Content-Range'], 'bytes 2-5/10')
        self.assertEqual(b''.join(response.streaming_content), b'2345')

    def test_local_track_returns_not_satisfiable_for_range_after_end(self):
        response = self.track.get_reponse_content('bytes=10-')

        self.assertEqual(response.status_code, 416)
        self.assertEqual(response['Content-Range'], 'bytes */10')

    def test_external_file_range_response_is_forwarded(self):
        track = Track()
        track.linkmusic = LinkMusic(
            url='https://example.test/audio.mp3',
            urlType='FILE',
            domained_name='example.test',
        )
        upstream_response = HttpResponse(status=206)
        upstream_response['Accept-Ranges'] = 'bytes'
        upstream_response['Content-Length'] = '4'
        upstream_response['Content-Range'] = 'bytes 2-5/10'

        with patch(
            'main.architecture.persistence.models.Track.UrlMusicStreamStrategy'
        ) as strategy_factory, patch.object(
            FileStreamExtract,
            'extract',
            return_value=(iter([b'2345']), 'file'),
        ) as extract, patch.object(
            FileStreamExtract,
            'response',
            upstream_response,
            create=True,
        ):
            strategy_factory.return_value.get_strategy.return_value = FileStreamExtract
            response = track.get_reponse_content('bytes=2-5')

        extract.assert_called_once_with('bytes=2-5')
        self.assertEqual(response.status_code, 206)
        self.assertEqual(response['Content-Length'], '4')
        self.assertEqual(response['Content-Range'], 'bytes 2-5/10')
        self.assertEqual(b''.join(response.streaming_content), b'2345')