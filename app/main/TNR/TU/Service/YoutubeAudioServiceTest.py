import os
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from django.test import TestCase, tag

from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.domain.common.service.YoutubeAudioService import YoutubeAudioService


@tag('unitaire')
class YoutubeAudioServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='youtube_user', password='test')
        self.other_user = User.objects.create_user(username='other_user', password='test')
        self.playlist = Playlist.objects.create(
            user=self.user,
            name='Playlist YouTube',
            typePlaylist='PLAYLIST_TYPE_MUSIC',
        )
        self.other_playlist = Playlist.objects.create(
            user=self.other_user,
            name='Other playlist',
            typePlaylist='PLAYLIST_TYPE_MUSIC',
        )
        self.downloader = MagicMock()

    @patch('main.domain.common.service.YoutubeAudioService.UserParametersFactory')
    def test_create_music_from_url_downloads_and_saves_music(
        self, mock_user_parameters_factory
    ):
        mock_user_parameters_factory.return_value.limit_music_per_playlist = 10
        mock_user_parameters_factory.return_value.limit_weight_file = 5

        def download_audio(url, temp_dir, max_filesize_bytes):
            mp3_path = os.path.join(temp_dir, 'download.mp3')
            with open(mp3_path, 'wb') as audio_file:
                audio_file.write(b'fake mp3')
            return 'Titre distant', mp3_path

        self.downloader.download_audio.side_effect = download_audio
        service = YoutubeAudioService(self.user, downloader=self.downloader)

        music = service.create_music_from_url(
            self.playlist,
            'https://www.youtube.com/watch?v=video-id',
            name='Mon morceau',
        )

        self.assertIsInstance(music, Music)
        self.assertEqual(music.playlist, self.playlist)
        self.assertEqual(music.alternativeName, 'mon-morceau')
        self.downloader.download_audio.assert_called_once()
        self.assertEqual(self.downloader.download_audio.call_args.kwargs['max_filesize_bytes'], 5 * 1024 * 1024)

        music.file.delete(save=False)

    @patch('main.domain.common.service.YoutubeAudioService.UserParametersFactory')
    def test_save_music_uses_downloaded_title_when_name_is_missing(
        self, mock_user_parameters_factory
    ):
        mock_user_parameters_factory.return_value.limit_music_per_playlist = 10
        mock_user_parameters_factory.return_value.limit_weight_file = 5

        with TemporaryDirectory() as temp_dir:
            mp3_path = os.path.join(temp_dir, 'download.mp3')
            with open(mp3_path, 'wb') as audio_file:
                audio_file.write(b'fake mp3')

            with patch('main.domain.brokers.message.ReduceBiteRateMessenger.reduce_bit_rate.apply_async'):
                music = YoutubeAudioService(self.user, self.downloader)._save_music(
                    self.playlist, 'Titre distant', mp3_path
                )

        self.assertEqual(music.alternativeName, 'titre-distant')
        music.file.delete(save=False)

    def test_create_music_from_url_rejects_invalid_urls(self):
        service = YoutubeAudioService(self.user, downloader=self.downloader)

        for url in ('', 'http://youtube.com/video', 'https://'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                service.create_music_from_url(self.playlist, url)

        self.downloader.download_audio.assert_not_called()

    def test_create_music_from_url_rejects_playlist_owned_by_another_user(self):
        service = YoutubeAudioService(self.user, downloader=self.downloader)

        with self.assertRaisesRegex(ValueError, 'Playlist introuvable'):
            service.create_music_from_url(self.other_playlist, 'https://youtube.com/video')

        self.downloader.download_audio.assert_not_called()

    @patch('main.domain.common.service.YoutubeAudioService.UserParametersFactory')
    def test_create_music_from_url_rejects_playlist_limit(self, mock_user_parameters_factory):
        mock_user_parameters_factory.return_value.limit_music_per_playlist = 0
        service = YoutubeAudioService(self.user, downloader=self.downloader)

        with self.assertRaisesRegex(ValueError, 'limite de musique par playlist'):
            service.create_music_from_url(self.playlist, 'https://youtube.com/video')

        self.downloader.download_audio.assert_not_called()

    @patch('main.domain.common.service.YoutubeAudioService.UserParametersFactory')
    def test_download_error_value_error_is_preserved(self, mock_user_parameters_factory):
        mock_user_parameters_factory.return_value.limit_music_per_playlist = 10
        self.downloader.download_audio.side_effect = ValueError('Le poids du fichier est trop lourd.')
        service = YoutubeAudioService(self.user, downloader=self.downloader)

        with self.assertRaisesRegex(ValueError, 'Le poids du fichier est trop lourd'):
            service.create_music_from_url(self.playlist, 'https://youtube.com/video')

    @patch('main.domain.common.service.YoutubeAudioService.UserParametersFactory')
    def test_download_unexpected_error_is_translated(self, mock_user_parameters_factory):
        mock_user_parameters_factory.return_value.limit_music_per_playlist = 10
        self.downloader.download_audio.side_effect = RuntimeError('network failure')
        service = YoutubeAudioService(self.user, downloader=self.downloader)

        with self.assertRaisesRegex(ValueError, "Impossible de telecharger l'audio"):
            service.create_music_from_url(self.playlist, 'https://youtube.com/video')

    @patch('main.domain.common.service.YoutubeAudioService.UserParametersFactory')
    def test_file_weight_limit_is_checked_after_download(self, mock_user_parameters_factory):
        mock_user_parameters_factory.return_value.limit_music_per_playlist = 10
        mock_user_parameters_factory.return_value.limit_weight_file = 0.000001
        service = YoutubeAudioService(self.user, downloader=self.downloader)

        with TemporaryDirectory() as temp_dir:
            mp3_path = os.path.join(temp_dir, 'download.mp3')
            with open(mp3_path, 'wb') as audio_file:
                audio_file.write(b'file larger than the configured limit')
            self.downloader.download_audio.return_value = ('Titre', mp3_path)

            with self.assertRaisesRegex(ValueError, 'poids du fichier est trop lourd'):
                service.create_music_from_url(self.playlist, 'https://youtube.com/video')

    @patch('main.domain.common.service.YoutubeAudioService.UserParametersFactory')
    def test_invalid_non_positive_file_limit_is_rejected_before_download(
        self, mock_user_parameters_factory
    ):
        mock_user_parameters_factory.return_value.limit_music_per_playlist = 10
        mock_user_parameters_factory.return_value.limit_weight_file = 0
        service = YoutubeAudioService(self.user, downloader=self.downloader)

        with self.assertRaisesRegex(ValueError, 'limite de poids audio est invalide'):
            service.create_music_from_url(self.playlist, 'https://youtube.com/video')

        self.downloader.download_audio.assert_not_called()