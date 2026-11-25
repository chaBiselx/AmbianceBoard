"""
Test d'intégration pour la route: Streaming d'une musique de proposition en attente
(/public/soundboards/<uuid:soundboard_uuid>/proposal/<uuid:proposal_uuid>/stream)
"""
from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistProposal import PlaylistProposal
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum

User = get_user_model()


@tag('integration')
class PublicProposalStreamMusicRouteTest(TestCase):
    """Tests pour la route de streaming d'une musique de proposition"""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='proposal_stream_owner', email='proposal_stream_owner@test.com', password='Test1234!')
        self.proposer = User.objects.create_user(username='proposal_stream_proposer', email='proposal_stream_proposer@test.com', password='Test1234!')
        self.other_user = User.objects.create_user(username='proposal_stream_other', email='proposal_stream_other@test.com', password='Test1234!')
        self.soundboard = SoundBoard.objects.create(user=self.owner, name='SB Proposal Stream', is_public=True)
        self.playlist = Playlist.objects.create(
            user=self.proposer,
            name='Playlist Proposal Stream',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )
        self.proposal = PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.proposer, 
        )

    def test_proposal_stream_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        response = self.client.get(
            reverse('publicProposalStreamMusic', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': self.proposal.uuid,
            })
        )
        self.assertEqual(response.status_code, 302)

    def test_proposal_stream_forbidden_for_non_proposer(self):
        """Un autre utilisateur authentifié ne peut pas accéder au stream de la proposition"""
        self.client.login(username='proposal_stream_other', password='Test1234!')
        response = self.client.get(
            reverse('publicProposalStreamMusic', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': self.proposal.uuid,
            })
        )
        self.assertEqual(response.status_code, 404)

    def test_proposal_stream_with_invalid_proposal_uuid(self):
        """Test avec un UUID de proposition inexistant"""
        self.client.login(username='proposal_stream_proposer', password='Test1234!')
        response = self.client.get(
            reverse('publicProposalStreamMusic', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': uuid.uuid4(),
            })
        )
        self.assertEqual(response.status_code, 404)

    def test_proposal_stream_metadata_only_without_cache_returns_404(self):
        """Sans cache préalable, une requête X-Metadata-Only doit échouer"""
        self.client.login(username='proposal_stream_proposer', password='Test1234!')
        response = self.client.get(
            reverse('publicProposalStreamMusic', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': self.proposal.uuid,
            }),
            HTTP_X_METADATA_ONLY='true',
        )
        self.assertEqual(response.status_code, 404)

    def test_range_request_reuses_cached_track_without_restarting_proposal(self):
        self.client.login(username='proposal_stream_proposer', password='Test1234!')
        track = Mock(id=123)
        track.get_reponse_content.return_value = HttpResponse(b'audio')

        with patch(
            'main.interface.ui.controller.public.playlistProposalViews.CacheFactory.get_default_cache'
        ) as cache_factory, patch(
            'main.interface.ui.controller.public.playlistProposalViews.PlaylistProposalRepository'
        ) as proposal_repository, patch(
            'main.interface.ui.controller.public.playlistProposalViews.TrackRepository'
        ) as track_repository, patch(
            'main.interface.ui.controller.public.playlistProposalViews.RandomizeTrackService'
        ) as randomize_service, patch(
            'main.interface.ui.controller.public.playlistProposalViews.SharedSoundboardService'
        ) as shared_service:
            cache = Mock()
            cache.get.return_value = track.id
            cache_factory.return_value = cache
            proposal_repository.return_value.get.return_value = self.proposal
            track_repository.return_value.get.return_value = track

            response = self.client.get(
                reverse('publicProposalStreamMusic', kwargs={
                    'soundboard_uuid': self.soundboard.uuid,
                    'proposal_uuid': self.proposal.uuid,
                }),
                HTTP_RANGE='bytes=10-19',
            )

        self.assertEqual(response.status_code, 200)
        track.get_reponse_content.assert_called_once_with('bytes=10-19')
        randomize_service.assert_not_called()
        shared_service.assert_not_called()
