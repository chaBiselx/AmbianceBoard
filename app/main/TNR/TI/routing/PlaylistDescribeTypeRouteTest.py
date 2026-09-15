"""
Test d'intégration pour la route: description des types de playlist (/playlist/type/describe)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@tag('integration')
class PlaylistDescribeTypeRouteTest(TestCase):
    """Tests pour la route playlist_describe_type (GET)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR

    def _url(self):
        return reverse('playlistDescribeType')

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_authenticated_user(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_returns_405_on_post_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 405)
