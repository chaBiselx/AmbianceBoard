from PIL import Image, ImageSequence
import os
import logging
from home.enum.ImageFormatEnum import ImageFormatEnum

 
class ImageResizer:
    max_size = 200  # Taille maximale du bord le plus grand par défaut
    
    def __init__(self, input_path, output_path):
        """
        Initialise le redimensionneur d'image avec le chemin d'entrée et de sortie.
        :param input_path: Chemin de l'image source.
        :param output_path: Chemin pour enregistrer l'image redimensionnée.
        """
        self.logger = logging.getLogger('home')
        
        self.input_path = input_path
        self.output_path = output_path
        self.logger.debug(f"ImageResizer initialized with input: {self.input_path}, output: {self.output_path}")
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"File {self.input_path} not found")
 
    def resize_image(self, max_size=200):
        """
        Redimensionne l'image afin que son bord le plus grand fasse max_size pixels.
        :param max_size: Taille maximale du bord le plus grand (par défaut 200px).
        """
        self.max_size = max_size
        self.logger.debug(f"resize_image STARTED : {self.input_path}")
        try:
            extension = os.path.splitext(self.input_path)[1].lower()
            resize_method = self._get_resize_method(extension)
            
            if not hasattr(self, resize_method):
                raise ValueError(f"Resize method {resize_method} not implemented for {extension}")
            # Appel de la méthode de redimensionnement appropriée
            resize_func = getattr(self, resize_method)
            resize_func()
            return self.output_path
        except Exception as e:
            self.logger.error(f"resize_image : Une erreur s'est produite : {e}") 
            return False

    def _get_resize_method(self, extension):
        """
        Redimensionne une image JPG.
        :param max_size: Taille maximale du bord le plus grand (par défaut 200px).
        """
        if extension in ImageFormatEnum.values():
            return ImageFormatEnum.methode_resizer().get(extension, "_resize_default")
        else:
            raise ValueError(f"Unsupported image format: {extension}")
        
    def _resize_default(self):
        """
        Redimensionne l'image par défaut en préservant la transparence.
        """
        # Ouvre l'image
        with Image.open(self.input_path) as img:
            self.logger.debug(f"L'image est ouverte : {self.input_path}")
            
            # Calculer le ratio de réduction
            is_resizing_needed, ratio = self._calcul_ratio(img.width, img.height)
            if is_resizing_needed:
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                
                # Redimensionner l'image en gardant les proportions
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_img.save(self.output_path)
                
                self.logger.debug(f"L'image a été redimensionnée ({ratio}) et sauvegardée sous : {self.output_path}")
                    
  
    
    def _resize_jpg(self):
        """
        Redimensionne une image. Si l'image d'entrée (JPG/JPEG) contient de la transparence,
        elle est convertie en PNG pour la préserver. Sinon, elle est sauvegardée en JPEG.
        """
        with Image.open(self.input_path) as img:
            self.logger.debug(f"L'image est ouverte : {self.input_path}")
            
            # Calculer le ratio de réduction
            is_resizing_needed, ratio = self._calcul_ratio(img.width, img.height)
            if is_resizing_needed:
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                
                if(img.mode in ('RGBA', 'LA', 'P')):
                    # Convertir en PNG pour préserver la transparence
                    self.output_path = os.path.splitext(self.output_path)[0] + '.png'
                    img = img.convert('RGBA')
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized_img.save(self.output_path, format='PNG')
                    self.logger.debug(f"L'image a été redimensionnée ({ratio}) et sauvegardée en PNG sous : {self.output_path}")
                else:
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized_img.save(self.output_path, format='JPEG')
                    self.logger.debug(f"L'image a été redimensionnée ({ratio}) et sauvegardée en JPEG sous : {self.output_path}")

    def _resize_ignore(self):
        """
        Ignore le redimensionnement pour les images SVG.
        """
        if self.output_path != self.input_path:
            os.rename(self.input_path, self.output_path)
        return self.output_path
    
    def _resize_gif(self):
        """
        Redimensionne une image GIF en préservant les frames.
        """
        with Image.open(self.input_path) as img:
            self.logger.debug(f"L'image GIF est ouverte : {self.input_path}")
            
            # Calculer le ratio de réduction
            is_resizing_needed, ratio = self._calcul_ratio(img.width, img.height)
            if is_resizing_needed:
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                
                frames = []
                for frame in ImageSequence.Iterator(img):
                    resized_frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    frames.append(resized_frame.convert('RGBA'))
                
                frames[0].save(self.output_path, save_all=True, append_images=frames[1:], loop=0)
                self.logger.debug(f"L'image GIF a été redimensionnée ({ratio}) et sauvegardée sous : {self.output_path}")

    def _calcul_ratio(self, width, height) -> tuple[bool, float]:
        """
        Calcule le ratio de réduction pour redimensionner l'image.
        :param width: Largeur de l'image.
        :param height: Hauteur de l'image.
        :return: Ratio de réduction.
        """
        ratio = min(self.max_size / width, self.max_size / height)
        if( ratio >= 1):
            return False, ratio
        return True, ratio
