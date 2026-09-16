"""
Test d'intégration pour la route: soundboardsDelete (DELETE /soundBoards/<uuid>/delete)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.architecture.persistence.models.SoundBoard import SoundBoard
import uuid

User = get_user_model()


@tag('integration')
class SoundboardsDeleteRouteTest(TestCase):
    """Tests pour la route soundboardsDelete (DELETE)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')

    def _url(self, soundboard_uuid=None):
        return reverse('soundboardsDelete', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid
        })

    def test_requires_authentication(self):
        response = self.client.delete(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_delete_returns_200_and_success_for_owner(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('success', data)

    def test_delete_removes_soundboard(self):
        self.client.login(username='owner', password='pw')
        self.client.delete(self._url())
        self.assertFalse(SoundBoard.objects.filter(pk=self.soundboard.pk).exists())

    def test_returns_404_for_nonexistent_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.delete(self._url(soundboard_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_soundboard(self):
        self.client.login(username='other', password='pw')
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, 404)

    def test_returns_405_on_get_request(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 405)
