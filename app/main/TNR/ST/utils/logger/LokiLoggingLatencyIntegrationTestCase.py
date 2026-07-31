"""Tests de stress verifies sur la latence HTTP quand Loki est lent/indisponible."""

import time
import statistics
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase, override_settings, tag
from django.urls import reverse

from main.domain.common.utils.logger.LoggerFactory import LoggerFactory


@tag('stress-test')
class LokiLoggingLatencyIntegrationTestCase(TestCase):
    """Couverture de non-regression orientee temps de reponse."""

    URL_NAME = 'publicListingSoundboard'

    def _reset_logger_cache_if_available(self):
        clear_cache = getattr(LoggerFactory, 'clear_default_logger_cache', None)
        if callable(clear_cache):
            clear_cache()

    def _measure_series(self, iterations=8, reset_logger_cache=False):
        client = Client()
        durations = []

        for _ in range(iterations):
            if reset_logger_cache:
                self._reset_logger_cache_if_available()

            start = time.perf_counter()
            response = client.get(reverse(self.URL_NAME))
            duration = time.perf_counter() - start

            self.assertEqual(response.status_code, 200)
            durations.append(duration)

        return durations

    def tearDown(self):
        # Evite les effets de bord quand un cache singleton des loggers existe.
        self._reset_logger_cache_if_available()
        super().tearDown()

    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',  # NOSONAR
        LOKI_BATCH_SIZE=10,
        LOKI_BATCH_TIMEOUT=5.0,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_loki_logger_initialization_is_not_blocking(self, mock_get):
        """Mesure de latence: l'initialisation d'un logger Loki ne doit pas bloquer."""

        def slow_healthcheck(*args, **kwargs):
            time.sleep(1.2)
            response = MagicMock()
            response.status_code = 200
            return response

        mock_get.side_effect = slow_healthcheck
        durations = []

        for idx in range(3):
            start = time.perf_counter()
            logger = LoggerFactory.create_logger(f'loki_init_latency_{idx}', 'loki')
            duration = time.perf_counter() - start
            durations.append(duration)
            if hasattr(logger, 'shutdown'):
                logger.shutdown()

        p50 = statistics.median(durations)
        self.assertLess(
            p50,
            0.4,
            msg=f"Initialisation Loki trop lente (p50={p50:.3f}s, valeurs={durations})",
        )

    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',  # NOSONAR
        LOKI_BATCH_SIZE=10,
        LOKI_BATCH_TIMEOUT=5.0,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_public_route_not_blocked_when_loki_is_slow_or_unavailable(self, mock_get, mock_post):
        """Mesure black-box: la route reste rapide meme si Loki est KO."""
        self._reset_logger_cache_if_available()

        def slow_healthcheck(*args, **kwargs):
            time.sleep(1.2)
            raise ConnectionError('loki unavailable')

        mock_get.side_effect = slow_healthcheck
        mock_post.side_effect = ConnectionError('loki push unavailable')

        durations = self._measure_series(iterations=10, reset_logger_cache=True)
        p95 = sorted(durations)[max(0, int(len(durations) * 0.95) - 1)]
        avg = statistics.mean(durations)

        self.assertLess(p95, 0.9)
        self.assertLess(avg, 0.7)

    @override_settings(
        LOGGER_TYPE='loki',
        LOKI_URL='http://test-loki:3100',  # NOSONAR
        LOKI_BATCH_SIZE=1,
        LOKI_BATCH_TIMEOUT=0.1,
    )
    @patch('main.domain.common.utils.logger.LokiLogger.requests.post')
    @patch('main.domain.common.utils.logger.LokiLogger.requests.get')
    def test_huge_loki_payload_is_sent_without_blocking(self, mock_get, mock_post):
        """Stress payload: envoi d'un log massif vers Loki sans blocage notable."""
        self._reset_logger_cache_if_available()

        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 204

        logger = LoggerFactory.create_logger('loki_huge_payload', 'loki')
        try:
            huge_message = 'X' * (2 * 1024 * 1024)

            start = time.perf_counter()
            logger.info(huge_message)
            enqueue_duration = time.perf_counter() - start

            time.sleep(0.4)

            self.assertTrue(mock_post.called)
            payload = mock_post.call_args[1]['json']
            sent_message = payload['streams'][0]['values'][0][1]

            self.assertEqual(len(sent_message), len(huge_message))
            self.assertEqual(sent_message[:128], huge_message[:128])
            self.assertEqual(sent_message[-128:], huge_message[-128:])
            self.assertLess(enqueue_duration, 0.2)
        finally:
            if hasattr(logger, 'shutdown'):
                logger.shutdown()


__all__ = ['LokiLoggingLatencyIntegrationTestCase']
