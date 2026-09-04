"""
Énumération des actions disponibles dans un script de soundboard.

Chaque action décrit une opération élémentaire exécutée par le moteur de script
côté client. L'ajout d'une nouvelle action se fait ici puis dans le
ScriptActionSpecRegistry (validation des paramètres) et dans le registre
d'actions du frontend (exécution).
"""

from typing import Dict
from .BaseEnum import BaseEnum


class ScriptActionEnum(BaseEnum):
    """
    Énumération des types d'actions d'une étape de script.

    - PLAY_PLAYLIST : joue une piste aléatoire d'une playlist
    - STOP_PLAYLIST : arrête la lecture d'une playlist
    - SET_VOLUME : modifie le volume d'une playlist
    - PLAY_TRACK : joue une piste précise (modélisé, non exécutable en v1)
    """

    PLAY_PLAYLIST = 'PlayPlaylist'
    STOP_PLAYLIST = 'StopPlaylist'
    SET_VOLUME = 'SetVolume'
    PLAY_TRACK = 'PlayTrack'

    def get_icon_class(self) -> str:
        """
        Récupère la classe d'icône FontAwesome associée à l'action.

        Returns:
            str: Classe CSS FontAwesome
        """
        icons: Dict[str, str] = {
            self.PLAY_PLAYLIST.name: "fa-solid fa-play",
            self.STOP_PLAYLIST.name: "fa-solid fa-stop",
            self.SET_VOLUME.name: "fa-solid fa-volume-high",
            self.PLAY_TRACK.name: "fa-solid fa-music",
        }
        return icons.get(self.name, "fa-solid fa-gears")

    @classmethod
    def names(cls) -> list:
        """
        Retourne la liste des noms techniques des actions.

        Returns:
            list: Noms des membres de l'énumération
        """
        return [member.name for member in cls]

    @classmethod
    def editable_actions(cls) -> list:
        """
        Retourne les actions proposées à l'édition côté client.

        PLAY_TRACK est modélisée mais pas encore exécutable côté client : on ne la propose pas à l'édition.

        Returns:
            list: Membres de l'énumération éditables
        """
        return [cls.PLAY_PLAYLIST]
