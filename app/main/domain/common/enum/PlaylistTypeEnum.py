"""
Énumération des types de playlists disponibles.

Définit les différents types de contenus audio supportés
avec leurs couleurs et icônes par défaut.
"""

from typing import Dict, Any
from .BaseEnum import BaseEnum
from django.templatetags.static import static 

class PlaylistTypeEnum(BaseEnum):
    """
    Énumération des types de playlists.
    
    Définit les trois types de playlists supportés :
    - INSTANT : Sons instantanés (effets sonores courts)
    - AMBIENT : Sons d'ambiance (boucles, atmosphères, musique intra-diegetique)
    - MUSIC : Musiques (morceaux musicaux, extra-diegetiques)
    """
    
    PLAYLIST_TYPE_INSTANT = 'Instant'
    PLAYLIST_TYPE_AMBIENT = 'Ambient'
    PLAYLIST_TYPE_MUSIC = 'Music'
    
    def get_default_color(self) -> Dict[str, str]:
        """
        Récupère les couleurs par défaut pour ce type de playlist.
        
        Returns:
            Dict[str, str]: Dictionnaire avec 'color' (couleur de fond) 
                           et 'colorText' (couleur du texte)
        """
        default_color ={
            self.PLAYLIST_TYPE_INSTANT.name: {'color': '#f40b0b', 'colorText': '#ffffff'},
            self.PLAYLIST_TYPE_AMBIENT.name: {'color': '#0bf40d', 'colorText': '#000000'},
            self.PLAYLIST_TYPE_MUSIC.name: {'color': '#0b10f4', 'colorText': '#ffffff'}
        }
        return default_color.get(self.name, {'color': '#000000', 'colorText': '#ffffff'})
 
    def get_icon_class(self) -> str:
        """
        Récupère la classe d'icône FontAwesome pour ce type de playlist.
        
        Returns:
            str: Classe CSS FontAwesome pour l'icône
        """
        default_class ={
            self.PLAYLIST_TYPE_INSTANT.name: "fa-solid fa-explosion",
            self.PLAYLIST_TYPE_AMBIENT.name: "fa-solid fa-dove",
            self.PLAYLIST_TYPE_MUSIC.name: "fa-solid fa-music"
        }
        return default_class.get(self.name, "fa-solid fa-sliders")