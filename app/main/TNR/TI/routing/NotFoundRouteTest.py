from unittest.mock import patch

from django.http import Http404, HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings, tag

from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.interface.ui.controller.general.generalViews import error_404


@tag('unitaire')
class NotFoundViewTest(SimpleTestCase):
    def test_handler_renders_custom_template_with_404_status(self):
        request = RequestFactory().get('/unknown-page')
        expected_response = HttpResponse(status=404)
        with patch(
            'main.interface.ui.controller.general.generalViews.render',
            return_value=expected_response,
        ) as render_mock:
            response = error_404(request, Http404())

        render_mock.assert_called_once_with(
            request, HtmlDefaultPageEnum.ERROR_404.value, status=404,
        )
        self.assertIs(response, expected_response)


@tag('integration')
@override_settings(DEBUG=False)
class NotFoundRouteTest(TestCase):
    def test_unknown_urls_render_custom_404_without_redirect(self):
        for url in (
            '/index.php',
            '/index.php?probe=1',
            '/faqq',
            '/unknown/path/',
            '/wp-admin/',
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                self.assertTemplateUsed(response, HtmlDefaultPageEnum.ERROR_404.value)
                self.assertNotIn('Location', response.headers)

    def test_post_to_unknown_url_renders_custom_404(self):
        response = self.client.post('/unknown-page', {'probe': '1'})

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, HtmlDefaultPageEnum.ERROR_404.value)