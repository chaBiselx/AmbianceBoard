"""
Test d'intégration pour la route: Suppression d'une proposition refusée
(/public/soundboards/<uuid:soundboard_uuid>/propose/<uuid:proposal_uuid>/dismiss)
"""
from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid

from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.PlaylistProposal import PlaylistProposal
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.PlaylistProposalStatusEnum import PlaylistProposalStatusEnum

User = get_user_model()


@tag('integration')
class PublicSoundboardDismissProposalRouteTest(TestCase):
    """Tests pour la route de suppression d'une proposition refusée"""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='dismiss_owner', email='dismiss_owner@test.com', password='Test1234!')
        self.proposer = User.objects.create_user(username='dismiss_proposer', email='dismiss_proposer@test.com', password='Test1234!')
        self.other_user = User.objects.create_user(username='dismiss_other', email='dismiss_other@test.com', password='Test1234!')
        self.soundboard = SoundBoard.objects.create(user=self.owner, name='SB Dismiss', is_public=True)
        self.playlist = Playlist.objects.create(
            user=self.proposer,
            name='Playlist Dismiss',
            typePlaylist=PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name,
            is_copiable=True,
        )

    def _create_proposal(self, status=PlaylistProposalStatusEnum.REFUSED.name):
        return PlaylistProposal.objects.create(
            playlist=self.playlist, soundboard=self.soundboard, proposer=self.proposer, status=status
        )

    def test_dismiss_proposal_requires_authentication(self):
        """Test que la route nécessite une authentification"""
        proposal = self._create_proposal()
        response = self.client.post(
            reverse('publicSoundboardDismissProposal', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': proposal.uuid,
            })
        )
        self.assertEqual(response.status_code, 302)

    def test_dismiss_refused_proposal_by_proposer(self):
        """Le proposeur peut supprimer sa proposition refusée"""
        proposal = self._create_proposal()
        self.client.login(username='dismiss_proposer', password='Test1234!')
        response = self.client.post(
            reverse('publicSoundboardDismissProposal', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': proposal.uuid,
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(PlaylistProposal.objects.filter(uuid=proposal.uuid).exists())

    def test_dismiss_proposal_forbidden_for_non_proposer(self):
        """Un autre utilisateur ne peut pas supprimer la proposition"""
        proposal = self._create_proposal()
        self.client.login(username='dismiss_other', password='Test1234!')
        response = self.client.post(
            reverse('publicSoundboardDismissProposal', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': proposal.uuid,
            })
        )
        self.assertEqual(response.status_code, 403)

    def test_dismiss_pending_proposal_returns_conflict(self):
        """Une proposition non refusée (PENDING) ne peut pas être supprimée"""
        proposal = self._create_proposal(status=PlaylistProposalStatusEnum.PENDING.name)
        self.client.login(username='dismiss_proposer', password='Test1234!')
        response = self.client.post(
            reverse('publicSoundboardDismissProposal', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': proposal.uuid,
            })
        )
        self.assertEqual(response.status_code, 409)

    def test_dismiss_proposal_with_invalid_uuid(self):
        """Test avec un UUID de proposition inexistant"""
        self.client.login(username='dismiss_proposer', password='Test1234!')
        response = self.client.post(
            reverse('publicSoundboardDismissProposal', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': uuid.uuid4(),
            })
        )
        self.assertEqual(response.status_code, 404)

    def test_dismiss_proposal_get_method_not_allowed(self):
        """Test que GET n'est pas autorisé sur cette route"""
        proposal = self._create_proposal()
        self.client.login(username='dismiss_proposer', password='Test1234!')
        response = self.client.get(
            reverse('publicSoundboardDismissProposal', kwargs={
                'soundboard_uuid': self.soundboard.uuid,
                'proposal_uuid': proposal.uuid,
            })
        )
        self.assertEqual(response.status_code, 405)
