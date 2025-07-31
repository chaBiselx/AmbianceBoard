"""
Énumération des types de transitions audio (fade).

Définit les différents types d'effets de transition
pour l'entrée et la sortie audio.
"""

from .BaseEnum import BaseEnum

class FadeEnum(BaseEnum):
    """
    Énumération des types d'effets de fade audio.
    
    Définit les courbes de transition pour les effets audio :
    - LINEAR : Transition linéaire uniforme
    - EASE : Transition standard avec accélération/décélération
    - EASE_IN : Transition avec accélération progressive
    - EASE_OUT : Transition avec décélération progressive
    - EASE_IN_QUAD : Transition quadratique en entrée
    - EASE_OUT_QUAD : Transition quadratique en sortie
    - EASE_IN_OUT_QUAD : Transition quadratique bidirectionnelle
    - EASE_OUT_CUBIC : Transition cubique en sortie
    """
    
    LINEAR = "linear"
    EASE = "ease"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_QUAD = "ease-in-quad"
    EASE_OUT_QUAD = "ease-out-quad"
    EASE_IN_OUT_QUAD = "ease-in-out-quad"
    EASE_OUT_CUBIC = "ease-out-cubic"