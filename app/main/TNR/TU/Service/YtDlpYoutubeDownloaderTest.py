from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, tag

from main.domain.common.exceptions.YoutubeDownloadException import YoutubeAudioTooLargeException
from main.domain.common.service.youtube.YtDlpYoutubeDownloader import YtDlpYoutubeDownloader


@tag('unitaire')
class YtDlpYoutubeDownloaderTest(SimpleTestCase):

    @patch('main.domain.common.service.youtube.YtDlpYoutubeDownloader.yt_dlp.YoutubeDL')
    def test_download_audio_raises_file_too_large_when_info_filesize_exceeds_limit(self, mock_youtube_dl):
        downloader = YtDlpYoutubeDownloader()

        info = {
            'title': 'sample',
            'filesize': 6 * 1024 * 1024,
        }

        ydl_instance = MagicMock()
        ydl_instance.extract_info.return_value = info
        ydl_instance.prepare_filename.return_value = 'sample.webm'

        context_manager = MagicMock()
        context_manager.__enter__.return_value = ydl_instance
        context_manager.__exit__.return_value = None
        mock_youtube_dl.return_value = context_manager

        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(YoutubeAudioTooLargeException) as context:
                downloader.download_audio(
                    url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    temp_dir=temp_dir,
                    max_filesize_bytes=5 * 1024 * 1024,
                )

        self.assertEqual(str(context.exception), 'Le poids du fichier est trop lourd.')

    @patch('main.domain.common.service.youtube.YtDlpYoutubeDownloader.yt_dlp.YoutubeDL')
    def test_download_audio_raises_file_too_large_when_partial_file_exceeds_limit(self, mock_youtube_dl):
        downloader = YtDlpYoutubeDownloader()

        info = {
            'title': 'sample',
        }

        ydl_instance = MagicMock()
        ydl_instance.extract_info.return_value = info

        context_manager = MagicMock()
        context_manager.__enter__.return_value = ydl_instance
        context_manager.__exit__.return_value = None
        mock_youtube_dl.return_value = context_manager

        with TemporaryDirectory() as temp_dir:
            part_file = Path(temp_dir) / 'sample.webm.part'
            part_file.write_bytes(b'x' * (6 * 1024 * 1024))

            ydl_instance.prepare_filename.return_value = str(Path(temp_dir) / 'sample.webm')

            with self.assertRaises(YoutubeAudioTooLargeException) as context:
                downloader.download_audio(
                    url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    temp_dir=temp_dir,
                    max_filesize_bytes=5 * 1024 * 1024,
                )

        self.assertEqual(str(context.exception), 'Le poids du fichier est trop lourd.')
