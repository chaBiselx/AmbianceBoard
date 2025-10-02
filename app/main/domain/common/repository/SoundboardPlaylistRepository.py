from typing import Any, Optional, List
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard



class SoundboardPlaylistRepository:

    def create(self, soundboard: SoundBoard, playlist: Playlist, order: int) -> SoundboardPlaylist:
        return SoundboardPlaylist.objects.create(
            SoundBoard=soundboard,
            Playlist=playlist,
            order=order
        )
        
    def get (self, soundboard: SoundBoard, playlist: Playlist) -> SoundboardPlaylist|None:
        try:
            return SoundboardPlaylist.objects.get(SoundBoard=soundboard, Playlist=playlist)
        except SoundboardPlaylist.DoesNotExist:
            return None 
    
    def get_first(self, soundboard: SoundBoard) -> SoundboardPlaylist|None:
        try:
            return SoundboardPlaylist.objects.filter(SoundBoard=soundboard).order_by('order').first()
        except SoundboardPlaylist.DoesNotExist:
            return None
        
    def get_all(self, soundboard: SoundBoard) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard).order_by('order')
    
    def get_order_greater_or_equal(self, soundboard: SoundBoard, order:int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, order__gte=order ).order_by('order')
        
    def delete(self, soundboard: SoundBoard, playlist: Playlist) -> bool:
        return self.soundboard_playlist_repository.delete(soundboard, playlist)

    def count(self, soundboard: SoundBoard) -> int:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard).count()
    
