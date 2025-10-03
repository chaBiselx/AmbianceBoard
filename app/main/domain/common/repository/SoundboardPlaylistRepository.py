from typing import Any, Optional, List
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from django.db import models



class SoundboardPlaylistRepository:

    def create(self, soundboard: SoundBoard, playlist: Playlist, order: int, section: int = 1) -> SoundboardPlaylist:
        return SoundboardPlaylist.objects.create(
            SoundBoard=soundboard,
            Playlist=playlist,
            order=order,
            section=section
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
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard).order_by('section', 'order')
    
    def get_max_section(self, soundboard: SoundBoard) -> int:
        max_section = SoundboardPlaylist.objects.filter(SoundBoard=soundboard).aggregate(models.Max('section'))['section__max']
        return max_section if max_section is not None else 1
    
    def get_all_by_section(self, soundboard: SoundBoard, section: int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, section=section).order_by('order')
    
    def get_order_greater_or_equal(self, soundboard: SoundBoard, order:int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, order__gte=order ).order_by('order')
    
    def get_order_greater_or_equal_by_section(self, soundboard: SoundBoard, order: int, section: int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, order__gte=order, section=section).order_by('order')
        
    def delete(self, soundboard: SoundBoard, playlist: Playlist) -> bool:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, Playlist=playlist).delete()

    def count(self, soundboard: SoundBoard) -> int:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard).count()
    
