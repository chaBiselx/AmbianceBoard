from .BaseEnum import BaseEnum

class ImageFormatEnum(BaseEnum): 

    JPG = ".jpg" 
    JPEG = ".jpeg"
    JFIF = ".jfif"
    PNG = ".png"
    SVG = ".svg"
    WEBP = ".webp"
    GIF = ".gif"


    
    @staticmethod
    def methode_resizer():
        """Retourne la méthode de redimensionnement appropriée pour chaque format d'image."""
        return {
            ImageFormatEnum.JPG.value: "_resize_jpg",
            ImageFormatEnum.JPEG.value: "_resize_jpg",
            ImageFormatEnum.SVG.value: "_resize_ignore",
            ImageFormatEnum.GIF.value: "_resize_gif",
            ImageFormatEnum.JFIF.value: "_resize_default",
            ImageFormatEnum.PNG.value: "_resize_default",
            ImageFormatEnum.WEBP.value: "_resize_default"
        }
