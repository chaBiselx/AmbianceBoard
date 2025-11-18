from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository


class SoundboardPlaylistService:
    
    def __init__(self, soundboard:SoundBoard):
        self.soundboard = soundboard
        self.soundboard_playlist_repository = SoundboardPlaylistRepository()
        
    def add(self, playlist:Playlist, order:int|None = None, section:int = 1):
        order = self.__check_order(order)

        if order is not None : 
            self.reorder_from(order, section)


        self.soundboard_playlist_repository.create(self.soundboard, playlist, order, section)
        return self
    
    def update(self, playlist:Playlist, order:int|None = None, section:int = 1):
        order = self.__check_order(order)
            
        if order is not None : 
            self.reorder_from(order, section)

        soundboard_playlist = self.soundboard_playlist_repository.get(self.soundboard, playlist)
        if soundboard_playlist is not None:
            soundboard_playlist.order = order
            soundboard_playlist.section = section
            soundboard_playlist.save()
        self.reorder_section(section)
        
        return self
    
    def __check_order(self, order:int|None = None):
        if(order is not None and order <= 0): 
            order = None
        if order is None:
            order = self._new_order()
        return order
    
    def remove(self, playlist:Playlist, section:int = 1):
        self.soundboard_playlist_repository.delete(self.soundboard, playlist)
        self.reorder_section(section)
        return self
            
    def _new_order(self):
        if self.soundboard_playlist_repository.count(self.soundboard) == 0:
            return 1
        else:
            return self.soundboard_playlist_repository.get_first(self.soundboard).order + 1
            
    def reorder_section(self, section=1):
        soundboard_playlists = self.soundboard_playlist_repository.get_all_by_section(self.soundboard, section)
        new_order = 1
        for soundboard_playlist in soundboard_playlists:
            soundboard_playlist.order = new_order
            soundboard_playlist.save()
            new_order += 1
        return self
    
    def reorder_from(self, order, section=1):
        soundboard_playlists = self.soundboard_playlist_repository.get_order_greater_or_equal_by_section(self.soundboard, order, section)
        new_order = order + 1
        for soundboard_playlist in soundboard_playlists:
            soundboard_playlist.order = new_order
            soundboard_playlist.save()
            new_order += 1
        return self
    