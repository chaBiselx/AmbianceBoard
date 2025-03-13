from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.strategy.PlaylistStrategy import PlaylistStrategy

class TypePlaylistFormater():
    type_playlist = None
    config = None
    
    def __init__(self, type_playlist):
        self.type_playlist = type_playlist
        self.config = PlaylistStrategy().get_strategy(self.type_playlist.name)
        
    def get_structured_data(self):
        return self.config.get_structure()
        
