from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.domain.common.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository


class SoundboardPlaylistService:
    
    def __init__(self, soundboard:SoundBoard):
        self.soundboard = soundboard
        self.soundboard_playlist_repository = SoundboardPlaylistRepository()
        
    def add(self, playlist:Playlist, order:int|None = None):
        order = self.__check_order(order)

        if order is not None : 
            self.reorder_from(order)


        self.soundboard_playlist_repository.create(self.soundboard, playlist, order)
        return self
    
    def update(self, playlist:Playlist, order:int|None = None):
        order = self.__check_order(order)
            
        if order is not None : 
            self.reorder_from(order)

        soundboard_playlist = self.soundboard_playlist_repository.get(self.soundboard, playlist)
        if soundboard_playlist is not None:
            soundboard_playlist.order = order
            soundboard_playlist.save()
        self.reorder()
        
        return self
    
    def __check_order(self, order:int|None = None):
        if(order is not None and order <= 0): 
            order = None
        if order is None:
            order = self._new_order()
        return order
    
    def remove(self, playlist:Playlist):
        self.soundboard_playlist_repository.delete(self.soundboard, playlist)
        self.reorder()
        return self
            
    def _new_order(self):
        if self.soundboard_playlist_repository.count(self.soundboard) == 0:
            return 1
        else:
            return self.soundboard_playlist_repository.get_first(self.soundboard) + 1
            
    def reorder(self):
        soundboard_playlists = self.soundboard_playlist_repository.get_all(self.soundboard)
        new_order = 1
        for soundboard_playlist in soundboard_playlists:
            soundboard_playlist.order = new_order
            soundboard_playlist.save()
            new_order += 1
            
        return self
    
    def reorder_from(self, order):
        soundboard_playlists = self.soundboard_playlist_repository.get_order_greater_or_equal(self.soundboard, order)
        new_order = order + 1
        for soundboard_playlist in soundboard_playlists:
            soundboard_playlist.order = new_order
            soundboard_playlist.save()
            new_order += 1
        return self
    