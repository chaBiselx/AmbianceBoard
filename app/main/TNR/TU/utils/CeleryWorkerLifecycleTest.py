from unittest import TestCase
from unittest.mock import patch

from django.test import tag

from main.architecture.messaging.tasks.celery import (
    log_worker_started,
    log_worker_stopped,
)


@tag("unitaire")
class CeleryWorkerLifecycleTestCase(TestCase):
    @patch(
        "main.architecture.messaging.tasks.celery.LoggerFactory.get_default_logger"
    )
    def test_worker_start_is_logged_with_its_name(self, get_logger):
        worker = type("Worker", (), {"hostname": "default@container"})()

        log_worker_started(sender=worker)

        get_logger.assert_called_once_with("celery")
        get_logger.return_value.info.assert_called_once_with(
            "Celery worker started: default@container"
        )

    @patch(
        "main.architecture.messaging.tasks.celery.LoggerFactory.get_default_logger"
    )
    def test_worker_shutdown_is_logged_with_its_name(self, get_logger):
        worker = type("Worker", (), {"hostname": "music-labeler@container"})()

        log_worker_stopped(sender=worker)

        get_logger.assert_called_once_with("celery")
        get_logger.return_value.warning.assert_called_once_with(
            "Celery worker stopping: music-labeler@container"
        )

    @patch(
        "main.architecture.messaging.tasks.celery.LoggerFactory.get_default_logger"
    )
    def test_worker_without_hostname_is_still_logged(self, get_logger):
        log_worker_started()

        get_logger.return_value.info.assert_called_once_with(
            "Celery worker started: unknown"
        )
