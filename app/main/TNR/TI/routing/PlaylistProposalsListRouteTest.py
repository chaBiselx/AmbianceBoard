"""
Test d'intégration pour la route: liste des propositions de playlist (/soundBoards/propositions)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.PlaylistProposal import PlaylistProposal
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PlaylistProposalsListRouteTest(TestCase):
    """Tests pour la route playlist_proposals_list (GET)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', email='owner@test.com', password='pw')  # NOSONAR
        self.other_user = User.objects.create_user(username='other', email='other@test.com', password='pw')  # NOSONAR

        self.soundboard = SoundBoard.objects.create(user=self.user, name='Board')
        self.other_soundboard = SoundBoard.objects.create(user=self.other_user, name='Autre board')

        self.playlist = Playlist.objects.create(
            user=self.other_user, name='Playlist proposée', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )
        self.other_playlist = Playlist.objects.create(
            user=self.user, name='Playlist autre soundboard', typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        )

        self.proposal = PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.other_user
        )
        self.other_proposal = PlaylistProposal.objects.create(
            playlist=self.other_playlist, soundboard=self.other_soundboard, proposer=self.user
        )

    def _url(self):
        return reverse('playlistProposalsList')

    def test_requires_authentication(self):
        response = self.client.get(self._url())
        self.assertIn(response.status_code, [302, 401, 403])

    def test_returns_200_for_authenticated_user(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_contains_pending_proposal_for_own_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertIn(self.playlist.name, content)

    def test_excludes_proposal_for_other_users_soundboard(self):
        self.client.login(username='owner', password='pw')
        response = self.client.get(self._url())
        content = response.content.decode('utf-8')
        self.assertNotIn(self.other_playlist.name, content)
