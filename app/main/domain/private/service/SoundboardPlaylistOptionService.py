from typing import List
from main.domain.private.dto.UpdateSoundPlaylistDto import UpdateSoundPlaylistDto
from main.domain.private.dto.ShortcutKeyboardPlaylistDto import ShortcutKeyboardPlaylistDto
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository


class SoundboardPlaylistOptionService:
    is_valid: bool = True
    stack_error: List[str] = []
    list_dto: List
    soundboard_playlist_repository: 'SoundboardPlaylistRepository'

    def __init__(self, update_sound_playlist_dto: List):
        self.list_dto = update_sound_playlist_dto
        self.soundboard_playlist_repository = SoundboardPlaylistRepository()

    def update_playlists(self) -> 'SoundboardPlaylistOptionService':
        for dto in self.list_dto:
            if(isinstance(dto, ShortcutKeyboardPlaylistDto)):
                self.update_playlist_shortcut(dto)
            elif(isinstance(dto, UpdateSoundPlaylistDto)):
                self.update_playlist_actionnable(dto)
        return self
        
    def update_playlist_actionnable(self, dto: UpdateSoundPlaylistDto):
        # Logique de mise à jour d'une seule playlist sonore
        try:
            soundboard_playlist = self.__validate_dto(dto)
        except ValueError:
            return self
        
        if dto.label == 'playable_by_players' and dto.value in [True, False]:
            soundboard_playlist.activable_by_player = dto.value

        soundboard_playlist.save()
        return self
    
    def update_playlist_shortcut(self, dto: ShortcutKeyboardPlaylistDto):
        # Logique de mise à jour d'une seule playlist sonore
        try:
            soundboard_playlist = self.__validate_dto(dto)
        except ValueError:
            return self
        
        if dto.shortcuts is None or isinstance(dto.shortcuts, list):
            soundboard_playlist.shortcut_keyboard = dto.shortcuts
    
        soundboard_playlist.save()
        return self
    
    def __validate_dto(self, dto) -> 'SoundboardPlaylist':
        soundboard_playlist = self.soundboard_playlist_repository.get_id(dto.soundboard_playlist_id)
        if( not soundboard_playlist):
            self.is_valid = False
            self.stack_error.append(f"SoundboardPlaylist with id {dto.soundboard_playlist_id} not found")
            raise ValueError("SoundboardPlaylist not found")
        
        if str(soundboard_playlist.Playlist.uuid) != dto.playlist_uuid and str(soundboard_playlist.SoundBoard.uuid) != dto.soundboard_uuid:
            self.is_valid = False
            self.stack_error.append(f"SoundboardPlaylist with id {dto.soundboard_playlist_id} does not match the provided soundboard_uuid and playlist_uuid")
            raise ValueError("SoundboardPlaylist does not match the provided soundboard_uuid and playlist_uuid")
        
        return soundboard_playlist
