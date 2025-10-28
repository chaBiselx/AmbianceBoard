from typing import Any, Dict,  Optional, List, TYPE_CHECKING
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.Playlist import Playlist
from django.db import models

if TYPE_CHECKING:
    from main.architecture.persistence.models.SoundBoard import SoundBoard




class SoundboardPlaylistRepository:

    def create(self, soundboard: "SoundBoard", playlist: Playlist, order: int, section: int = 1) -> SoundboardPlaylist:
        return SoundboardPlaylist.objects.create(
            SoundBoard=soundboard,
            Playlist=playlist,
            order=order,
            section=section
        )
        
    def get (self, soundboard: "SoundBoard", playlist: Playlist) -> SoundboardPlaylist|None:
        try:
            return SoundboardPlaylist.objects.get(SoundBoard=soundboard, Playlist=playlist)
        except SoundboardPlaylist.DoesNotExist:
            return None 
        
    def get_id(self, id) -> SoundboardPlaylist|None:
        try:
            return SoundboardPlaylist.objects.get(pk=id)
        except SoundboardPlaylist.DoesNotExist:
            return None 
    
    def get_first(self, soundboard: "SoundBoard") -> SoundboardPlaylist|None:
        try:
            return SoundboardPlaylist.objects.filter(SoundBoard=soundboard).order_by('order').first()
        except SoundboardPlaylist.DoesNotExist:
            return None
        
    def get_all(self, soundboard: "SoundBoard") -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard).order_by('section', 'order')
    
    def get_all_playable(self, soundboard: "SoundBoard") -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, activable_by_player=True).order_by('section', 'order')
    
    def get_playlist_formated(self, soundboard: "SoundBoard") -> Any:
        list_playlist = self.get_all(soundboard)
        dict_section = {}
        max_section = self.get_max_section(soundboard)
        for section in range(1, max_section + 1):
            dict_section[section] = []
        
        for sp in list_playlist:
            dict_section[sp.section].append(sp.Playlist)
        
        # Stocker les informations sur le soundboard pour usage ultérieur si nécessaire
        soundboard.dict_section = dict_section
        soundboard.max_section = max_section
        
        # Retourner le dictionnaire pour pouvoir l'itérer dans le template
        return dict_section.items()
    
    def get_soundboard_playlist_formated(self, soundboard: "SoundBoard") -> Any:
        list_playlist = self.get_all(soundboard)
        dict_section = {}
        for sp in list_playlist:
            if sp.section not in dict_section:
                dict_section[sp.section] = []
            dict_section[sp.section].append(sp)
  
        return dict_section.items()
    
    def get_soundboard_playlist_for_player_formated(self, soundboard: "SoundBoard") -> Any:
        list_playlist = self.get_all_playable(soundboard)
        dict_p_s = {}
        for sp in list_playlist:
            if sp.section not in dict_p_s:
                dict_p_s[sp.section] = []
            dict_p_s[sp.section].append(sp.Playlist)
  
        return dict_p_s.items()
    
    def get_max_section(self, soundboard: "SoundBoard") -> int:
        max_section = SoundboardPlaylist.objects.filter(SoundBoard=soundboard).aggregate(models.Max('section'))['section__max']
        return max_section if max_section is not None else 1
    
    def get_all_by_section(self, soundboard: "SoundBoard", section: int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, section=section).order_by('order')
    
    def get_order_greater_or_equal(self, soundboard: "SoundBoard", order:int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, order__gte=order ).order_by('order')
    
    def get_order_greater_or_equal_by_section(self, soundboard: "SoundBoard", order: int, section: int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, order__gte=order, section=section).order_by('order')
        
    def delete(self, soundboard: "SoundBoard", playlist: Playlist) -> bool:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard, Playlist=playlist).delete()

    def count(self, soundboard: "SoundBoard") -> int:
        return SoundboardPlaylist.objects.filter(SoundBoard=soundboard).count()
    
