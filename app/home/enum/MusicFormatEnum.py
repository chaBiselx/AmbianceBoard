"""
Énumération des formats audio supportés.

Définit les extensions de fichiers audio acceptées
par l'application pour l'upload de musiques.
"""

from .BaseEnum import BaseEnum

class MusicFormatEnum(BaseEnum):
    """
    Énumération des formats de fichiers audio supportés.
    
    Définit les extensions de fichiers audio acceptées :
    - MP3 : Format audio compressé le plus courant
    - WAV : Format audio non compressé haute qualité
    - OGG : Format audio ouvert compressé
    """
    
    MP3 = ".mp3"
    WAV = ".wav"
    OGG = ".ogg"