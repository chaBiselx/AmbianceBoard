"""
Test d'intégration pour la route: description des types de playlist (/playlist/type/describe)
"""
from django.test import tag
from django.urls import reverse

from main.TNR.Fixtures.BaseTestCases import AuthenticatedTestCase


@tag('integration')
class PlaylistDescribeTypeRouteTest(AuthenticatedTestCase):
    """Tests pour la route playlist_describe_type (GET)"""

    def setUp(self):
        super().setUp()

    def _url(self):
        return reverse('playlistDescribeType')

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_authenticated_user(self):
        self.login()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_405_on_post_request(self):
        self.login()
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 405)
