"""
Énumération des options de fade pour les playlists.

Définit les différentes options pour activer ou désactiver
les effets de fade in/out sur les playlists.
"""

from .BaseEnum import BaseEnum
from .FadeEnum import FadeEnum
from django.utils.translation import gettext_lazy as _

class FadePlaylistEnum(BaseEnum):
    """
    Énumération des options de fade pour les playlists.
    
    Définit les options disponibles pour gérer les transitions audio :
    - DEFAULT : Utilise la configuration par défaut selon le type de playlist
    - FadeEnum.* : Force explicitement une courbe de fade
    """
    
    DEFAULT = "enum.fade_playlist.default"

    @classmethod
    def _get_translated_fade_labels(cls):
        return {
            cls.DEFAULT.name: _("enum.fade_playlist.default"),
            FadeEnum.DISABLED.name: _("enum.fade_curve.disabled"),
            FadeEnum.LINEAR.name: _("enum.fade_curve.linear"),
            FadeEnum.EASE.name: _("enum.fade_curve.ease"),
            FadeEnum.EASE_IN.name: _("enum.fade_curve.ease_in"),
            FadeEnum.EASE_OUT.name: _("enum.fade_curve.ease_out"),
            FadeEnum.EASE_IN_QUAD.name: _("enum.fade_curve.ease_in_quad"),
            FadeEnum.EASE_OUT_QUAD.name: _("enum.fade_curve.ease_out_quad"),
            FadeEnum.EASE_IN_OUT_QUAD.name: _("enum.fade_curve.ease_in_out_quad"),
            FadeEnum.EASE_OUT_CUBIC.name: _("enum.fade_curve.ease_out_cubic"),
        }

    @classmethod
    def _get_fr_labels(cls):
        """Compatibilité avec les tests existants.

        Le nom historique est conservé, mais les labels proviennent désormais
        du système de traduction Django.
        """
        return cls._get_translated_fade_labels()

    @classmethod
    def convert_to_choices(cls):
        """Retourne les choix pour Playlist.fadeIn/fadeOut.

        Les valeurs stockées sont les noms d'enum :
        - DEFAULT
        - puis toute la liste de FadeEnum (LINEAR, EASE, ...)
        """
        choices = []
        translated_labels = cls._get_fr_labels()
        default_labels = {
            cls.DEFAULT.name: _("enum.fade_playlist.default"),
        }
        choices.append(
            (
                cls.DEFAULT.name,
                translated_labels.get(cls.DEFAULT.name, default_labels[cls.DEFAULT.name]),
            )
        )
        choices.extend((fade.name, translated_labels.get(fade.name, fade.value)) for fade in FadeEnum)
        
        return choices
