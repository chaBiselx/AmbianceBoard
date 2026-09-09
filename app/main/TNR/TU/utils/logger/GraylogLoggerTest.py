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
    def test_log_empty_message_falls_back_to_repr(self, mock_sendto):
        """Un message vide (ex: str(exception) sans argument) ne doit jamais produire un short_message vide"""
        self.logger.error("")

        event = self._get_sent_event(mock_sendto)
        self.assertNotEqual(event['short_message'], "")
        self.assertEqual(event['short_message'], repr(""))

    @patch('socket.socket.sendto')
    def test_log_exception_without_message_falls_back_to_repr(self, mock_sendto):
        """Une exception sans message (str(e) == '') ne doit pas produire un short_message vide"""
        self.logger.error(str(ValueError()))

        event = self._get_sent_event(mock_sendto)
        self.assertNotEqual(event['short_message'], "")
