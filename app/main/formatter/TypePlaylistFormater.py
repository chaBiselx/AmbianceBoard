from typing import Any, Dict
from main.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.strategy.PlaylistStrategy import PlaylistStrategy
from main.strategy.playlistConfig.AbstractConfig import AbstractConfig


class TypePlaylistFormater():
    type_playlist: PlaylistTypeEnum
    config: AbstractConfig
    
    def __init__(self, type_playlist: PlaylistTypeEnum) -> None:
        self.type_playlist = type_playlist
        self.config = PlaylistStrategy().get_strategy(self.type_playlist.name)
        
    def get_structured_data(self) -> Dict[str, Any]:
        return self.config.get_structure()
        
