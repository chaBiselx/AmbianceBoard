from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, tag

from main.domain.common.strategy.urlMusicStream.FileStreamExtract import FileStreamExtract


@tag('unitaire')
class FileStreamExtractTest(SimpleTestCase):
    @patch('main.domain.common.strategy.urlMusicStream.FileStreamExtract.requests.get')
    def test_extract_forwards_range_header_to_upstream(self, get):
        response = Mock(status_code=206, headers={'Content-Range': 'bytes 10-19/100'})
        response.iter_content.return_value = [b'partial-audio']
        get.return_value = response
        extractor = FileStreamExtract(SimpleNamespace(
            urlType='FILE',
            url='https://example.test/audio.mp3',
            domained_name='example.test',
        ))

        stream, stream_type = extractor.extract('bytes=10-19')

        get.assert_called_once_with(
            'https://example.test/audio.mp3',
            headers={'Range': 'bytes=10-19'},
            stream=True,
            timeout=10,
        )
        self.assertEqual(stream_type, 'file')
        self.assertEqual(response.status_code, extractor.response.status_code)
        self.assertEqual(list(stream), [b'partial-audio'])
        response.close.assert_called_once()