from django.test import TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.repository.AsyncDownloadJobRepository import AsyncDownloadJobRepository


@tag('unitaire')
class AsyncDownloadJobRepositoryRepositoryTest(TestCase):
    def setUp(self):
        self.repository = AsyncDownloadJobRepository()
        self.user = User.objects.create_user(username='job-user', password='pw')  # NOSONAR
        self.playlist = Playlist.objects.create(name='Job Playlist', user=self.user)

    def test_create_defaults_source_to_youtube(self):
        job = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/example',
        )

        self.assertEqual('youtube', job.source)

    def test_create_accepts_explicit_source(self):
        job = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://vimeo.com/example',
            source='vimeo',
        )

        self.assertEqual('vimeo', job.source)