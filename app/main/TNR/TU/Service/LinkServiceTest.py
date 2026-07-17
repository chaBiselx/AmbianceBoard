from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase, tag

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.User import User
from main.domain.private.service.LinkService import LinkService


@tag('unitaire')
class LinkServiceTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='link-service-user', password='pw')  # NOSONAR
        self.playlist = Playlist.objects.create(name='Link Playlist', user=self.user)

    @patch('main.domain.private.service.LinkService.process_async_download_job.apply_async')
    @patch('main.domain.private.service.LinkService.UserParametersFactory')
    @patch('main.domain.private.service.LinkService.AsyncDownloadJobRepository.set_task_id')
    @patch('main.domain.private.service.LinkService.AsyncDownloadJobRepository.create')
    @patch('main.domain.private.service.LinkService.AsyncDownloadJobRepository.count_active', return_value=0)
    @patch('main.domain.private.service.LinkService.TrackRepository.get_count', return_value=0)
    def test_save_form_enqueues_async_download_job_with_job_uuid_only(
        self,
        _mock_track_count,
        _mock_active_count,
        mock_create_job,
        mock_set_task_id,
        mock_user_parameters_factory,
        mock_apply_async,
    ):
        request = self.factory.post(
            '/',
            {
                'url': 'https://www.youtube.com/watch?v=abc123',
                'alternativeName': 'My title',
            },
        )
        request.user = self.user

        mock_user_parameters_factory.return_value = SimpleNamespace(limit_music_per_playlist=10)
        mock_job = SimpleNamespace(uuid='job-uuid')
        mock_create_job.return_value = mock_job
        mock_apply_async.return_value = SimpleNamespace(id='celery-task-id')

        service = LinkService(request)

        result = service.save_form(self.playlist)

        self.assertIsNone(result)
        mock_apply_async.assert_called_once_with(
            args=['job-uuid'],
            queue='default',
            priority=1,
        )
        mock_set_task_id.assert_called_once_with(mock_job, 'celery-task-id')