from typing import Any, Dict
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.strategy.PlaylistStrategy import PlaylistStrategy
from home.strategy.playlistConfig.AbstractConfig import AbstractConfig


class TypePlaylistFormater():
    type_playlist: PlaylistTypeEnum
    config: AbstractConfig
    
    def __init__(self, type_playlist: PlaylistTypeEnum) -> None:
        self.type_playlist = type_playlist
        self.config = PlaylistStrategy().get_strategy(self.type_playlist.name)
        
    def get_structured_data(self) -> Dict[str, Any]:
        return self.config.get_structure()
        
