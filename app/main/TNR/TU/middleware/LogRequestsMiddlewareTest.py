from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, tag

from main.architecture.middleware.LogRequestsMiddleware import LogRequestsMiddleware


@tag('unitaire')
class LogRequestsMiddlewareTest(SimpleTestCase):
    def test_exception_logs_error_and_retries_request(self):
        fallback_response = HttpResponse(status=503)
        get_response = Mock(side_effect=[Exception('request failed'), fallback_response])
        middleware = LogRequestsMiddleware(get_response)
        request = RequestFactory().get('/')

        with patch('main.architecture.middleware.LogRequestsMiddleware.logging.error') as log_error:
            response = middleware(request)

        self.assertIs(response, fallback_response)
        self.assertEqual(get_response.call_count, 2)
        log_error.assert_called_once_with(
            'Erreur dans le middleware de logging request failed'
        )