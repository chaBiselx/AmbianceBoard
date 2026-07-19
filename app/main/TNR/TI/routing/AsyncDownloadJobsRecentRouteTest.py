"""
Test d'intégration pour la route: recent async download jobs (/account/downloads/recent)
"""
from datetime import timedelta

from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.AsyncDownloadJob import AsyncDownloadJob
from main.architecture.persistence.repository.AsyncDownloadJobRepository import AsyncDownloadJobRepository

User = get_user_model()


@tag('integration')
class AsyncDownloadJobsRecentRouteTest(TestCase):
    """Tests pour la route des téléchargements asynchrones récents"""

    def setUp(self):
        self.client = Client()
        self.repository = AsyncDownloadJobRepository()

        self.user = User.objects.create_user(
            username='recent-job-user',
            email='recent@example.com',
            password='testpass123'
        )
        self.playlist = Playlist.objects.create(name='User Playlist', user=self.user)

        self.other_user = User.objects.create_user(
            username='other-job-user',
            email='other@example.com',
            password='testpass123'
        )
        self.other_playlist = Playlist.objects.create(name='Other Playlist', user=self.other_user)

    def test_recent_route_requires_auth(self):
        response = self.client.get(reverse('asyncDownloadJobsRecent'))
        self.assertIn(response.status_code, [302, 401, 403])

    def test_recent_route_shows_only_current_user_recent_jobs(self):
        self.client.login(username='recent-job-user', password='testpass123')

        recent_job = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/user-recent'
        )
        old_job = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/user-old'
        )
        other_user_recent_job = self.repository.create(
            user=self.other_user,
            playlist=self.other_playlist,
            url='https://youtu.be/other-recent'
        )

        now = timezone.now()
        AsyncDownloadJob.objects.filter(pk=recent_job.pk).update(updated_at=now - timedelta(hours=1))
        AsyncDownloadJob.objects.filter(pk=old_job.pk).update(updated_at=now - timedelta(hours=28))
        AsyncDownloadJob.objects.filter(pk=other_user_recent_job.pk).update(updated_at=now - timedelta(hours=1))

        response = self.client.get(reverse('asyncDownloadJobsRecent'))

        self.assertEqual(response.status_code, 200)
        page_objects = list(response.context['page_objects'])
        self.assertEqual([recent_job.pk], [job.pk for job in page_objects])

    def test_navbar_button_visible_only_when_recent_job_exists(self):
        self.client.login(username='recent-job-user', password='testpass123')
        route = reverse('asyncDownloadJobsRecent')

        response_without_jobs = self.client.get(route)
        self.assertEqual(response_without_jobs.status_code, 200)
        self.assertNotContains(response_without_jobs, route)

        recent_job = self.repository.create(
            user=self.user,
            playlist=self.playlist,
            url='https://youtu.be/user-visible'
        )
        AsyncDownloadJob.objects.filter(pk=recent_job.pk).update(updated_at=timezone.now() - timedelta(hours=2))

        response_with_job = self.client.get(route)
        self.assertEqual(response_with_job.status_code, 200)
        self.assertContains(response_with_job, route)
