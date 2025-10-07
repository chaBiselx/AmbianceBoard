from typing import List
from main.domain.private.dto.UpdateSoundPlaylistDto import UpdateSoundPlaylistDto
from main.domain.common.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository


class SoundboardPlaylistOptionService:
    is_valid: bool = True
    stack_error: List[str] = []
    list_dto: List[UpdateSoundPlaylistDto]
    soundboard_playlist_repository: 'SoundboardPlaylistRepository'

    def __init__(self, update_sound_playlist_dto: List[UpdateSoundPlaylistDto]):
        self.list_dto = update_sound_playlist_dto
        self.soundboard_playlist_repository = SoundboardPlaylistRepository()

    def update_playlists(self) -> 'SoundboardPlaylistOptionService':
        for dto in self.list_dto:
            self.update_playlist(dto)
        return self
        
    def update_playlist(self, dto: UpdateSoundPlaylistDto):
        # Logique de mise à jour d'une seule playlist sonore
        soundboard_playlist = self.soundboard_playlist_repository.get_id(dto.soundboard_playlist_id)
        if( not soundboard_playlist):
            self.is_valid = False
            self.stack_error.append(f"SoundboardPlaylist with id {dto.soundboard_playlist_id} not found")
            return self
        
        if str(soundboard_playlist.Playlist.uuid) != dto.playlist_uuid and str(soundboard_playlist.SoundBoard.uuid) != dto.soundboard_uuid:
            self.is_valid = False
            self.stack_error.append(f"SoundboardPlaylist with id {dto.soundboard_playlist_id} does not match the provided soundboard_uuid and playlist_uuid")
            return self
        
        if dto.label == 'playable_by_players' and dto.value in [True, False]:
            soundboard_playlist.activable_by_player = dto.value

        soundboard_playlist.save()
        print('Updated SoundboardPlaylist:', soundboard_playlist.id)
        print('soundboard_playlist.activable_by_player:', soundboard_playlist.activable_by_player)
        return self
