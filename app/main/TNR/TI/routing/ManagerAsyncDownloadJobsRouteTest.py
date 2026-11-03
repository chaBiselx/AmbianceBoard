from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase, tag
from django.urls import reverse
from django.utils import timezone

from main.architecture.persistence.models.AsyncDownloadJob import AsyncDownloadJob
from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.enum.AsyncDownloadJobStatusEnum import AsyncDownloadJobStatusEnum
from main.domain.common.enum.PermissionEnum import PermissionEnum

User = get_user_model()


@tag("integration")
class ManagerAsyncDownloadJobsRouteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(
            username="download-manager",
            email="manager@example.com",
            password="testpass123",
        )
        role_group, _ = Group.objects.get_or_create(name="ROLE_ADMIN")
        self.manager.groups.add(role_group)
        manager_permission, _ = Permission.objects.get_or_create(
            codename=PermissionEnum.MANAGER_EXECUTE_BATCHS.name,
            content_type=ContentType.objects.get_for_model(Group),
            defaults={"name": "Manager execute batchs"},
        )
        self.manager.user_permissions.add(manager_permission)
        self.user = User.objects.create_user(
            username="download-owner",
            email="owner@example.com",
            password="testpass123",
        )
        self.playlist = Playlist.objects.create(name="Downloads playlist", user=self.user)

    def create_job(self, status=AsyncDownloadJobStatusEnum.PENDING.name):
        return AsyncDownloadJob.objects.create(
            user=self.user,
            playlist=self.playlist,
            url="https://youtu.be/example",
            status=status,
        )

    def test_listing_requires_authentication(self):
        response = self.client.get(reverse("managerAsyncDownloadJobs"))
        self.assertEqual(response.status_code, 302)

    def test_listing_requires_manager_permission(self):
        user = User.objects.create_user(
            username="regular-user",
            email="regular@example.com",
            password="testpass123",
        )
        self.client.login(username=user.username, password="testpass123")
        response = self.client.get(reverse("managerAsyncDownloadJobs"))
        self.assertIn(response.status_code, [302, 403])

    def test_listing_shows_jobs_and_retry_action_only_for_pending(self):
        self.client.login(username=self.manager.username, password="testpass123")
        pending_job = self.create_job()
        completed_job = self.create_job(AsyncDownloadJobStatusEnum.SUCCESS.name)

        response = self.client.get(reverse("managerAsyncDownloadJobs"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.playlist.name)
        self.assertContains(response, pending_job.url)
        self.assertContains(response, completed_job.url)
        self.assertContains(response, reverse("managerAsyncDownloadJobRetry", args=[pending_job.uuid]))
        self.assertNotContains(response, reverse("managerAsyncDownloadJobRetry", args=[completed_job.uuid]))

    def test_listing_filters_by_status_and_date_range(self):
        self.client.login(username=self.manager.username, password="testpass123")
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        old_pending_job = self.create_job()
        matching_pending_job = self.create_job()
        other_status_job = self.create_job(AsyncDownloadJobStatusEnum.SUCCESS.name)
        AsyncDownloadJob.objects.filter(pk=old_pending_job.pk).update(
            created_at=timezone.make_aware(datetime.combine(yesterday, time.min))
        )
        AsyncDownloadJob.objects.filter(pk=matching_pending_job.pk).update(
            created_at=timezone.make_aware(datetime.combine(today, time.min))
        )
        AsyncDownloadJob.objects.filter(pk=other_status_job.pk).update(
            created_at=timezone.make_aware(datetime.combine(today, time.min))
        )

        response = self.client.get(
            reverse("managerAsyncDownloadJobs"),
            {
                "status": AsyncDownloadJobStatusEnum.PENDING.name,
                "date_from": today.isoformat(),
                "date_to": today.isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [matching_pending_job.pk],
            [job.pk for job in response.context["page_objects"]],
        )
        self.assertContains(response, 'value="PENDING" selected')
        self.assertContains(response, 'name="date_from"')
        self.assertContains(response, 'name="date_to"')
        self.assertContains(response, f'value="{today.isoformat()}"')

    def test_listing_pagination_keeps_filters_applied(self):
        self.client.login(username=self.manager.username, password="testpass123")
        AsyncDownloadJob.objects.bulk_create([
            AsyncDownloadJob(
                user=self.user,
                playlist=self.playlist,
                url=f"https://youtu.be/example-{index}",
                status=AsyncDownloadJobStatusEnum.PENDING.name,
            )
            for index in range(51)
        ])

        response = self.client.get(
            reverse("managerAsyncDownloadJobs"),
            {"status": AsyncDownloadJobStatusEnum.PENDING.name, "date_from": timezone.localdate().isoformat(), "page": 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_objects"]), 1)
        self.assertContains(response, 'value="PENDING" selected')
        self.assertContains(response, 'name="date_from"')

    def test_listing_returns_no_jobs_when_date_range_is_reversed(self):
        self.create_job()
        self.client.login(username=self.manager.username, password="testpass123")

        response = self.client.get(
            reverse("managerAsyncDownloadJobs"),
            {"date_from": "2026-11-02", "date_to": "2026-11-01"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_objects"]), 0)
        self.assertContains(response, 'name="date_from"')
        self.assertContains(response, 'name="date_to"')
        self.assertContains(response, 'value="2026-11-02"')
        self.assertContains(response, 'value="2026-11-01"')

    @patch("main.interface.ui.controller.manager.managerAsyncDownloadJobViews.process_async_download_job.apply_async")
    def test_pending_job_can_be_retried(self, mock_apply_async):
        self.client.login(username=self.manager.username, password="testpass123")
        job = self.create_job()
        job.error_message = "Old error"
        job.save(update_fields=["error_message"])
        mock_apply_async.return_value = SimpleNamespace(id="new-celery-task-id")

        response = self.client.post(
            reverse("managerAsyncDownloadJobRetry", args=[job.uuid])
        )

        self.assertRedirects(response, reverse("managerAsyncDownloadJobs"))
        mock_apply_async.assert_called_once_with(
            args=[str(job.uuid)],
            queue="default",
            priority=1,
        )
        job.refresh_from_db()
        self.assertEqual(job.celery_task_id, "new-celery-task-id")
        self.assertEqual(job.error_message, "")

    @patch("main.interface.ui.controller.manager.managerAsyncDownloadJobViews.process_async_download_job.apply_async")
    def test_non_pending_job_cannot_be_retried(self, mock_apply_async):
        self.client.login(username=self.manager.username, password="testpass123")
        job = self.create_job(AsyncDownloadJobStatusEnum.SUCCESS.name)

        response = self.client.post(
            reverse("managerAsyncDownloadJobRetry", args=[job.uuid])
        )

        self.assertRedirects(response, reverse("managerAsyncDownloadJobs"))
        mock_apply_async.assert_not_called()
        job.refresh_from_db()
        self.assertEqual(job.status, AsyncDownloadJobStatusEnum.SUCCESS.name)

    def test_retry_requires_post(self):
        self.client.login(username=self.manager.username, password="testpass123")
        job = self.create_job()

        response = self.client.get(
            reverse("managerAsyncDownloadJobRetry", args=[job.uuid])
        )

        self.assertEqual(response.status_code, 405)
