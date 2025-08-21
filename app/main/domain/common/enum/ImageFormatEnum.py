"""
Énumération des formats d'images supportés.

Définit les extensions d'images acceptées et les méthodes
de redimensionnement appropriées pour chaque format.
"""

from typing import Dict
from .BaseEnum import BaseEnum

class ImageFormatEnum(BaseEnum):
    """
    Énumération des formats d'images supportés.
    
    Définit les extensions d'images acceptées pour les icônes
    de soundboards et playlists, avec leurs méthodes de traitement spécifiques.
    """

    JPG = ".jpg" 
    JPEG = ".jpeg"
    JFIF = ".jfif"
    PNG = ".png"
    SVG = ".svg"
    WEBP = ".webp"
    GIF = ".gif"

    @staticmethod
    def methode_resizer() -> Dict[str, str]:
        """
        Retourne la méthode de redimensionnement appropriée pour chaque format d'image.
        
        Returns:
            Dict[str, str]: Dictionnaire mappant les extensions aux méthodes de redimensionnement
        """
        return {
            ImageFormatEnum.JPG.value: "_resize_jpg",
            ImageFormatEnum.JPEG.value: "_resize_jpg",
            ImageFormatEnum.SVG.value: "_resize_ignore",
            ImageFormatEnum.GIF.value: "_resize_gif",
            ImageFormatEnum.JFIF.value: "_resize_default",
            ImageFormatEnum.PNG.value: "_resize_default",
            ImageFormatEnum.WEBP.value: "_resize_default"
        }
