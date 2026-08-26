import uuid
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Track import Track
from main.architecture.persistence.repository.filters.MusicFilter import MusicFilter
from main.architecture.persistence.repository.TrackRepository import TrackRepository
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository
from main.interface.ui.forms.private.MusicForm import MusicForm
from main.domain.common.factory.UserParametersFactory import UserParametersFactory
from main.domain.common.service.SoundBoardService import SoundBoardService
from main.domain.common.enum.MusicFormatEnum import MusicFormatEnum
from main.architecture.persistence.repository.PlaylistProposalRepository import PlaylistProposalRepository
from main.domain.common.enum.PlaylistProposalStatusEnum import PlaylistProposalStatusEnum


class RandomizeTrackService:
    
    def __init__(self, request):
        self.request = request
        self.track_repository = TrackRepository()
        self.soundboard_playlist_repository = SoundboardPlaylistRepository()

    def _is_playlist_in_soundboard(self, soundboard, playlist_uuid) -> bool:
        return self.soundboard_playlist_repository.get_playlist_in_soundboard_by_uuid(soundboard, playlist_uuid) is not None
        
    def get_specific_private(self, soundboard_uuid:uuid, playlist_uuid:int, music_id: int) -> Music|None :
        soundboard = (SoundBoardService(self.request)).get_soundboard(soundboard_uuid)
        if not soundboard or not self._is_playlist_in_soundboard(soundboard, playlist_uuid):
            return None
        return self.track_repository.get(music_id, playlist_uuid)

    def generate_private(self, soundboard_uuid:uuid, playlist_uuid:int)-> Music|None :
        soundboard = (SoundBoardService(self.request)).get_soundboard(soundboard_uuid)
        if not soundboard or not self._is_playlist_in_soundboard(soundboard, playlist_uuid):
            return None
        return self.track_repository.get_random_private(playlist_uuid, self.request.user)
    
    def get_specific_public(self, soundboard_uuid:uuid, playlist_uuid:int, music_id: int) -> Music|None :
        soundboard = (SoundBoardService(self.request)).get_public_soundboard(soundboard_uuid)
        if not soundboard or not self._is_playlist_in_soundboard(soundboard, playlist_uuid):
            return None
        return self.track_repository.get(music_id, playlist_uuid)
    
    def generate_public(self, soundboard_uuid:uuid, playlist_uuid:int)-> Music|None :
        soundboard = (SoundBoardService(self.request)).get_public_soundboard(soundboard_uuid)
        if not soundboard or not self._is_playlist_in_soundboard(soundboard, playlist_uuid):
            return None
        return self.track_repository.get_random_public(playlist_uuid)

    def get_shared(self, soundboard_uuid:uuid, playlist_uuid:int, token:str, music_id: int)-> Music|None :
        soundboard = (SoundBoardService(self.request)).get_soundboard_from_shared_soundboard(soundboard_uuid, token)
        if not soundboard or not self._is_playlist_in_soundboard(soundboard, playlist_uuid):
            return None
        return self.track_repository.get(music_id, playlist_uuid)

    def generate_public_proposal(self, soundboard_uuid:uuid, proposal_uuid:uuid) -> Music|None :
        """Génère une piste aléatoire pour la playlist d'une proposition en attente, réservée à son auteur."""
        proposal = PlaylistProposalRepository().get(proposal_uuid)
        if not proposal or str(proposal.soundboard.uuid) != str(soundboard_uuid):
            return None
        if proposal.status != PlaylistProposalStatusEnum.PENDING.name or proposal.proposer != self.request.user:
            return None
        return self.track_repository.get_random_public(proposal.playlist.uuid)

    def get_shared_proposal(self, soundboard_uuid:uuid, token:str, proposal_uuid:uuid, music_id: int) -> Music|None :
        """Récupère une piste précise d'une proposition en attente pour les auditeurs d'une session partagée."""
        soundboard = (SoundBoardService(self.request)).get_soundboard_from_shared_soundboard(soundboard_uuid, token)
        if not soundboard:
            return None
        proposal = PlaylistProposalRepository().get(proposal_uuid)
        if not proposal or str(proposal.soundboard.uuid) != str(soundboard_uuid) or proposal.status != PlaylistProposalStatusEnum.PENDING.name:
            return None
        return self.track_repository.get(music_id, proposal.playlist.uuid)
     
        
