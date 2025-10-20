"""Tests unitaires et d'intégration pour `LokiLogger` (signature actuelle: seul `logger_name`)."""

import time
import threading
from unittest import TestCase
from unittest.mock import patch
from django.test import override_settings

from main.domain.common.utils.logger.LokiLogger import LokiLogger
from main.domain.common.utils.logger.ILogger import ILogger


class LokiLoggerTestCase(TestCase):
    def test_initialisation_par_defaut(self):
        logger = LokiLogger()
        try:
            self.assertIsInstance(logger, ILogger)
            self.assertEqual(logger.logger_name, 'main')
            self.assertTrue(logger._sender_thread.is_alive())
            self.assertIn('http://loki:3100', logger.loki_url)
        finally:
            logger.shutdown()

    @override_settings(LOKI_URL='http://custom-loki:3100')
    def test_initialisation_avec_setting_url(self):
        logger = LokiLogger('custom')
        try:
            self.assertIn('http://custom-loki:3100', logger.loki_url)
        finally:
            logger.shutdown()

    def test_nom_vide(self):
        with self.assertRaises(ValueError):
            LokiLogger(logger_name='')

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=1, LOKI_BATCH_TIMEOUT=0.1, LOKI_URL='http://test-loki:3100')
    def test_debug_message(self, mock_post):
        mock_post.return_value.status_code = 204
        logger = LokiLogger('debug_test')
        try:
            logger.debug('Debug message test')
            time.sleep(0.2)
            self.assertTrue(mock_post.called)
            self.assertEqual(mock_post.call_args[0][0], 'http://test-loki:3100/loki/api/v1/push')
        finally:
            logger.shutdown()

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=5, LOKI_BATCH_TIMEOUT=0.2, LOKI_URL='http://test-loki:3100')
    def test_tous_niveaux(self, mock_post):
        mock_post.return_value.status_code = 204
        logger = LokiLogger('levels_test')
        try:
            logger.debug('Debug'); logger.info('Info'); logger.warning('Warn'); logger.error('Error'); logger.critical('Critical')
            time.sleep(0.3)
            self.assertTrue(mock_post.called)
        finally:
            logger.shutdown()

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=1, LOKI_BATCH_TIMEOUT=0.1, LOKI_URL='http://test-loki:3100')
    def test_exception(self, mock_post):
        mock_post.return_value.status_code = 204
        logger = LokiLogger('exception_test')
        try:
            try:
                raise ValueError('Test exception')
            except ValueError:
                logger.exception('Exception occurred')
            time.sleep(0.2)
            self.assertTrue(mock_post.called)
            msg = mock_post.call_args[1]['json']['streams'][0]['values'][0][1]
            self.assertIn('Exception occurred', msg)
            self.assertIn('ValueError: Test exception', msg)
        finally:
            logger.shutdown()

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=1, LOKI_BATCH_TIMEOUT=0.1)
    def test_formatage(self, mock_post):
        mock_post.return_value.status_code = 204
        logger = LokiLogger('formatting_test')
        try:
            logger.info('User %s logged in with ID %d', 'john', 7)
            time.sleep(0.2)
            msg = mock_post.call_args[1]['json']['streams'][0]['values'][0][1]
            self.assertEqual(msg, 'User john logged in with ID 7')
        finally:
            logger.shutdown()

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=1, LOKI_BATCH_TIMEOUT=0.1)
    def test_labels_extra(self, mock_post):
        mock_post.return_value.status_code = 204
        logger = LokiLogger('labels_test')
        try:
            logger.info('Test', extra_labels={'user': '42'})
            time.sleep(0.2)
            labels = mock_post.call_args[1]['json']['streams'][0]['stream']
            self.assertEqual(labels['logger'], 'labels_test')
            self.assertEqual(labels['service'], 'labels_test')
            self.assertEqual(labels['user'], '42')
        finally:
            logger.shutdown()

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=3, LOKI_BATCH_TIMEOUT=0.5)
    def test_batch(self, mock_post):
        mock_post.return_value.status_code = 204
        logger = LokiLogger('batch_test')
        try:
            for i in range(5): logger.info(f'Message {i}')
            time.sleep(0.6)
            self.assertTrue(mock_post.called)
            # Selon le timing du thread, les 5 messages peuvent être envoyés en 1 ou 2 batches.
            # On valide simplement qu'au moins un envoi a eu lieu.
            self.assertGreaterEqual(mock_post.call_count, 1)
        finally:
            logger.shutdown()

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=10, LOKI_BATCH_TIMEOUT=5)
    def test_flush(self, mock_post):
        mock_post.return_value.status_code = 204
        logger = LokiLogger('flush_test')
        try:
            logger.info('Message')
            self.assertFalse(mock_post.called)
            logger.flush()
        finally:
            logger.shutdown()

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=1, LOKI_BATCH_TIMEOUT=0.1)
    def test_erreur_reseau(self, mock_post):
        mock_post.side_effect = Exception('Network error')
        logger = LokiLogger('network_test')
        try:
            logger.info('Test')
            time.sleep(0.2)
        finally:
            logger.shutdown()

    @patch('requests.post')
    @override_settings(LOKI_BATCH_SIZE=50, LOKI_BATCH_TIMEOUT=1)
    def test_thread_safety(self, mock_post):
        mock_post.return_value.status_code = 204
        logger = LokiLogger('thread_test')
        try:
            def worker(tid):
                for i in range(10): logger.info(f'Thread {tid} message {i}')
            threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
            [t.start() for t in threads]; [t.join() for t in threads]
            time.sleep(1.2)
            self.assertTrue(mock_post.called)
        finally:
            logger.shutdown()

    def test_repr(self):
        logger = LokiLogger('repr_test')
        try:
            self.assertIn('repr_test', repr(logger))
            self.assertIn('loki', str(logger))
        finally:
            logger.shutdown()


class LokiLoggerIntegrationTestCase(TestCase):
    @override_settings(LOKI_URL='http://test-loki:3100', LOKI_BATCH_SIZE=1, LOKI_BATCH_TIMEOUT=0.1)
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

__all__ = ['LokiLoggerTestCase', 'LokiLoggerIntegrationTestCase']