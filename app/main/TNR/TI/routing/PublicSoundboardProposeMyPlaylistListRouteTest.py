"""
Test d'intégration pour la route: Liste des playlists proposables par l'utilisateur
(/public/soundboards/<uuid:soundboard_uuid>/propose/my-playlists)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Track import Track
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PublicSoundboardProposeMyPlaylistListRouteTest(TestCase):
    """Tests pour la route de liste des playlists proposables"""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='propose_list_owner', email='propose_list_owner@test.com', password='Test1234!')
        self.proposer = User.objects.create_user(username='propose_list_proposer', email='propose_list_proposer@test.com', password='Test1234!')
        self.soundboard = SoundBoard.objects.create(user=self.owner, name='SB Propose List', is_public=True)

        self.playlist = Playlist.objects.create(
            user=self.proposer,
            name='Playlist proposable',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        Track.objects.create(playlist=self.playlist, alternativeName='Track proposable')

    def test_propose_list_without_auth_shows_connexion_modal(self):
        """Sans authentification, la vue affiche la modale d'invitation à se connecter"""
        response = self.client.get(
            reverse('publicSoundboardProposeMyPlaylistList', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)

    def test_propose_list_accessible_when_authenticated(self):
        """L'utilisateur authentifié, non propriétaire, obtient la liste de ses playlists proposables"""
        self.client.login(username='propose_list_proposer', password='Test1234!')
        response = self.client.get(
            reverse('publicSoundboardProposeMyPlaylistList', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Playlist proposable')

    def test_propose_list_forbidden_for_owner(self):
        """Le propriétaire du soundboard ne peut pas consulter cette liste sur son propre board"""
        self.client.login(username='propose_list_owner', password='Test1234!')
        response = self.client.get(
            reverse('publicSoundboardProposeMyPlaylistList', kwargs={'soundboard_uuid': self.soundboard.uuid})
        )
        self.assertEqual(response.status_code, 404)

    def test_propose_list_with_invalid_uuid(self):
        """Test avec un UUID de soundboard inexistant"""
        self.client.login(username='propose_list_proposer', password='Test1234!')
        response = self.client.get(
            reverse('publicSoundboardProposeMyPlaylistList', kwargs={'soundboard_uuid': uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_propose_list_filters_by_playlist_type(self):
        """Un filtre par type de playlist inconnu ne doit pas faire échouer la requête"""
        self.client.login(username='propose_list_proposer', password='Test1234!')
        response = self.client.get(
            reverse('publicSoundboardProposeMyPlaylistList', kwargs={'soundboard_uuid': self.soundboard.uuid}),
            {'playlistType': 'unknown-type', 'page': 1}
        )
        self.assertEqual(response.status_code, 200)
