from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard


class SoundboardPlaylistService:
    
    def __init__(self, soundboard:SoundBoard):
        self.soundboard = soundboard
        
    def add(self, playlist:Playlist, order:int|None = None):
        order = self.__check_order(order)

        if order is not None : 
            self.reorder_from(order)
        
        SoundboardPlaylist.objects.create(
            SoundBoard=self.soundboard,
            Playlist=playlist,
            order=order
        )
        return self
    
    def update(self, playlist:Playlist, order:int|None = None):
        order = self.__check_order(order)
            
        if order is not None : 
            self.reorder_from(order)
        
        soundboard_playlist = SoundboardPlaylist.objects.get(SoundBoard=self.soundboard, Playlist=playlist)
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
        SoundboardPlaylist.objects.get(SoundBoard=self.soundboard, Playlist=playlist).delete()
        self.reorder()
        return self
            
    def _new_order(self):
        if SoundboardPlaylist.objects.filter(SoundBoard=self.soundboard).count() == 0:
            return 1
        else:
            return SoundboardPlaylist.objects.filter(SoundBoard=self.soundboard).order_by('-order').first().order + 1
            
    def reorder(self):
        soundboard_playlists = SoundboardPlaylist.objects.filter(SoundBoard=self.soundboard).order_by('order')
        new_order = 1
        for soundboard_playlist in soundboard_playlists:
            soundboard_playlist.order = new_order
            soundboard_playlist.save()
            new_order += 1
            
        return self
    
    def reorder_from(self, order):
        soundboard_playlists = SoundboardPlaylist.objects.filter(SoundBoard=self.soundboard, order__gte=order ).order_by('order')
        new_order = order + 1
        for soundboard_playlist in soundboard_playlists:
            soundboard_playlist.order = new_order
            soundboard_playlist.save()
            new_order += 1
        return self
    