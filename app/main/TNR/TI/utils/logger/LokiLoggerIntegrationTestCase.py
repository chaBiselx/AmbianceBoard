"""Tests unitaires et d'intégration pour `LokiLogger` (signature actuelle: seul `logger_name`)."""

import time
import threading
from unittest import TestCase
from unittest.mock import patch
from django.test import override_settings, tag

from main.domain.common.utils.logger.LokiLogger import LokiLogger
from main.domain.common.utils.logger.ILogger import ILogger


@tag('integration')
class LokiLoggerIntegrationTestCase(TestCase):
    @override_settings(LOKI_URL='http://test-loki:3100', LOKI_BATCH_SIZE=1, LOKI_BATCH_TIMEOUT=0.1) # NOSONAR
    @patch('requests.post')
    def test_factory_loki(self, mock_post):
        mock_post.return_value.status_code = 204
        from main.domain.common.utils.logger.LoggerFactory import LoggerFactory
        logger = LoggerFactory.create_logger('factory_loki', 'loki')
        try:
            logger.info('Factory message')
            time.sleep(0.2)
            self.assertTrue(mock_post.called)
        finally:
            logger.shutdown()

__all__ = ['LokiLoggerIntegrationTestCase']