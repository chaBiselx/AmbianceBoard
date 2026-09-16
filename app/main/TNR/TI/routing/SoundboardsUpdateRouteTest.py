"""
Test d'intégration pour la route: soundboardsUpdate (GET/POST /soundBoards/<uuid>/update)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardTag import SoundboardTag
import uuid

User = get_user_model()


@tag('integration')
class SoundboardsUpdateRouteTest(TestCase):
    """Tests pour la route soundboardsUpdate (GET/POST)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')
        self.tag = SoundboardTag.objects.create(name='Tag', is_active=True)

    def _url(self, soundboard_uuid=None):
        return reverse('soundboardsUpdate', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid
        })

    def test_get_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_get_returns_200_for_owner(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_get_returns_404_for_nonexistent_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(soundboard_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_get_returns_404_for_other_users_soundboard(self):
        self.client.login(username='other', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_post_valid_data_redirects_to_list(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(), {'name': 'Updated name', 'color': '#000000', 'colorText': '#ffffff', 'tags': [self.tag.pk]})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('soundboardsList'))
        self.soundboard.refresh_from_db()
        self.assertEqual(self.soundboard.name, 'Updated name')

    def test_post_returns_404_for_nonexistent_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(soundboard_uuid=uuid.uuid4()), {'name': 'Updated name'})
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_data_returns_200_with_form_errors(self):
        self.client.login(username='owner', password='pw')
        response = self.client.post(self._url(), {'name': ''})
        self.assertEqual(response.status_code, 200)
        self.soundboard.refresh_from_db()
        self.assertEqual(self.soundboard.name, 'Board')
