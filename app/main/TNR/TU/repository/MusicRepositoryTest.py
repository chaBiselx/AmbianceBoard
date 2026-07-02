from django.test import TestCase, tag
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.MusicRepository import MusicRepository


@tag('unitaire')
class MusicRepositoryTest(TestCase):
    CONTENT_MP3 = 'audio/mp3'

    def setUp(self):
        patcher = patch('main.domain.brokers.message.ReduceBiteRateMessenger.reduce_bit_rate.apply_async')
        self.mock_apply_async = patcher.start()
        self.addCleanup(patcher.stop)

        self.user = User.objects.create_user(username='music-repo-user', password='pw')  # NOSONAR
        self.playlist = Playlist.objects.create(name='Music Repo Playlist', user=self.user)
        self.repository = MusicRepository()

        self.shared_file = SimpleUploadedFile('shared.mp3', b'shared-content', content_type=self.CONTENT_MP3)
        self.unique_file = SimpleUploadedFile('unique.mp3', b'unique-content', content_type=self.CONTENT_MP3)

        self.shared_music = Music.objects.create(
            fileName='shared',
            alternativeName='Shared',
            file=self.shared_file,
            playlist=self.playlist,
        )
        self.other_shared_music = Music.objects.create(
            fileName='shared-copy',
            alternativeName='Shared Copy',
            file=self.unique_file,
            playlist=self.playlist,
        )
        Music.objects.filter(id=self.other_shared_music.id).update(file=self.shared_music.file.name)
        self.other_shared_music.refresh_from_db()

        self.unique_music = Music.objects.create(
            fileName='unique',
            alternativeName='Unique',
            file=SimpleUploadedFile('unique-2.mp3', b'unique-2-content', content_type=self.CONTENT_MP3),
            playlist=self.playlist,
        )

    def test_is_file_used_elsewhere_returns_true_when_another_music_uses_same_file(self):
        self.assertTrue(self.repository.is_file_used_elsewhere(self.shared_music.file, self.shared_music.id))

    def test_is_file_used_elsewhere_returns_false_when_file_is_unique(self):
        self.assertFalse(self.repository.is_file_used_elsewhere(self.unique_music.file, self.unique_music.id))

    def test_is_file_used_elsewhere_returns_false_when_no_file(self):
        self.assertFalse(self.repository.is_file_used_elsewhere(None, self.shared_music.id))