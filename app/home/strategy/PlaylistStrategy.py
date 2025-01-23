from .playlistConfig.ConfigInstant import ConfigInstant
from .playlistConfig.ConfigAmbient import ConfigAmbient
from .playlistConfig.ConfigMusic import ConfigMusic
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum

class PlaylistStrategy:
    """Fabrique qui retourne la bonne stratégie selon le type de configuration."""
    _strategies = {
        PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name: ConfigInstant(),
        PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name: ConfigAmbient(),
        PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name: ConfigMusic(),
    }
    
    def get_strategy(self, config_type) -> dict:
        return self._strategies.get(
            config_type,
            ConfigInstant()  # Une stratégie par défaut si le type est inconnu
        )
        
        