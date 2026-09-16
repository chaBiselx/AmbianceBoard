"""
Tests unitaires pour GraylogLogger.
Tests de l'envoi de messages GELF, notamment le message classique et le cas du message vide.
"""

import json
from unittest.mock import patch
from django.test import tag
from unittest import TestCase as UnitTestCase

from main.domain.common.utils.logger.GraylogLogger import GraylogLogger


@tag('unitaire')
class GraylogLoggerTestCase(UnitTestCase):
    """Tests unitaires pour GraylogLogger"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.logger = GraylogLogger('test_graylog')

    def _get_sent_event(self, mock_sendto) -> dict:
        payload, _address = mock_sendto.call_args[0]
        return json.loads(payload.decode('utf-8'))

    @patch('socket.socket.sendto')
    def test_log_classic_message(self, mock_sendto):
        """Un message classique doit être transmis tel quel dans short_message"""
        self.logger.info("Message classique de test")

        event = self._get_sent_event(mock_sendto)
        self.assertEqual(event['short_message'], "Message classique de test")
        self.assertEqual(event['_logger'], 'test_graylog')
        self.assertEqual(event['_log_level'], 'info')

    @patch('socket.socket.sendto')
    def test_log_empty_message_is_ignored(self, mock_sendto):
        """Un message vide ou vide encadré par des guillemets ne doit pas être envoyé à Graylog"""
        self.logger.error("")
        self.logger.error("''")

        self.assertEqual(mock_sendto.call_count, 0)

    @patch('socket.socket.sendto')
    def test_log_exception_without_message_is_ignored(self, mock_sendto):
        """Une exception sans message (str(e) == '') ne doit pas être envoyée à Graylog"""
        self.logger.error(str(ValueError()))

        self.assertEqual(mock_sendto.call_count, 0)
