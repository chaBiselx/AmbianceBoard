"""
Test d'intégration pour la route: organizeSoundboard (GET /soundBoards/<uuid>/organize)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
import uuid

User = get_user_model()


@tag('integration')
class OrganizeSoundboardRouteTest(TestCase):
    """Tests pour la route organizeSoundboard (GET)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')
        self.playlist = Playlist.objects.create(
            user=self.user,
            name='Playlist',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
        )
        SoundboardPlaylist.objects.create(SoundBoard=self.soundboard, Playlist=self.playlist, section=1, order=1)

    def _url(self, soundboard_uuid=None):
        return reverse('organizeSoundboard', kwargs={
            'soundboard_uuid': soundboard_uuid or self.soundboard.uuid
        })

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_owner(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Html/Soundboard/soundboard_organize.html')

    def test_returns_404_for_nonexistent_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url(soundboard_uuid=uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_returns_404_for_other_users_soundboard(self):
        self.client.login(username='other', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_context_contains_soundboard_playlists(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertIn(self.playlist.name, content)
