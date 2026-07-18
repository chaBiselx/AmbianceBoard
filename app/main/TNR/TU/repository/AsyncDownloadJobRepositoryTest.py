from django.test import TestCase, tag
from django.utils import timezone

from datetime import timedelta

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.architecture.persistence.models.AsyncDownloadJob import AsyncDownloadJob
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

    def test_get_recent_jobs_for_user_only_returns_jobs_in_last_24h_for_current_user(self):
        other_user = User.objects.create_user(username='other-user', password='pw')  # NOSONAR
        other_playlist = Playlist.objects.create(name='Other Playlist', user=other_user)

        recent_job = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/recent',
        )
        old_job = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/old',
        )
        other_user_recent_job = self.repository.create(
            user=other_user,
            playlist=other_playlist,
            url='https://youtu.be/other',
        )

        now = timezone.now()
        AsyncDownloadJob.objects.filter(pk=recent_job.pk).update(updated_at=now - timedelta(hours=2))
        AsyncDownloadJob.objects.filter(pk=old_job.pk).update(updated_at=now - timedelta(hours=26))
        AsyncDownloadJob.objects.filter(pk=other_user_recent_job.pk).update(updated_at=now - timedelta(hours=1))

        jobs = list(self.repository.get_recent_jobs_for_user(self.user))
        self.assertEqual([recent_job.pk], [job.pk for job in jobs])

    def test_count_recent_jobs_for_user(self):
        recent_job_1 = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/recent-1',
        )
        recent_job_2 = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/recent-2',
        )
        old_job = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/old-2',
        )

        now = timezone.now()
        AsyncDownloadJob.objects.filter(pk=recent_job_1.pk).update(updated_at=now - timedelta(hours=3))
        AsyncDownloadJob.objects.filter(pk=recent_job_2.pk).update(updated_at=now - timedelta(hours=4))
        AsyncDownloadJob.objects.filter(pk=old_job.pk).update(updated_at=now - timedelta(hours=30))

        count = self.repository.count_recent_jobs_for_user(self.user)
        self.assertEqual(2, count)