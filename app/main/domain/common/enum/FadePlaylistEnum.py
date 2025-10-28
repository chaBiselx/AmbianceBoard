"""
Énumération des options de fade pour les playlists.

Définit les différentes options pour activer ou désactiver
les effets de fade in/out sur les playlists.
"""

from .BaseEnum import BaseEnum

class FadePlaylistEnum(BaseEnum):
    """
    Énumération des options de fade pour les playlists.
    
    Définit les options disponibles pour gérer les transitions audio :
    - DEFAULT : Utilise le paramètre par défaut de l'utilisateur
    - YES : Active l'effet de fade
    - NO : Désactive l'effet de fade
    """
    
    DEFAULT = "Par défaut"
    YES = "Oui"
    NO = "Non"
