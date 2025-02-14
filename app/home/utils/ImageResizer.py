from PIL import Image
import os
import logging

 
class ImageResizer:
    def __init__(self, input_path, output_path):
        """
        Initialise le redimensionneur d'image avec le chemin d'entrée et de sortie.
        :param input_path: Chemin de l'image source.
        :param output_path: Chemin pour enregistrer l'image redimensionnée.
        """
        self.logger = logging.getLogger('home')
        
        self.input_path = input_path
        self.output_path = output_path
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"File {self.input_path} not found")
 
    def resize_image(self, max_size=200):
        """
        Redimensionne l'image afin que son bord le plus grand fasse max_size pixels.
        :param max_size: Taille maximale du bord le plus grand (par défaut 300px).
        """
        self.logger.debug(f"resize_image STARTED : {max_size}")
        
        try:
            # Ouvre l'image
            with Image.open(self.input_path) as img:
                self.logger.debug(f"L'image est ouverte : {self.input_path}")
                # Calculer le ratio de réduction
                ratio = min(max_size / img.width, max_size / img.height)
                if(ratio < 1):
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
    
                    # Redimensionner l'image en gardant les proportions
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
                    # Sauvegarder l'image redimensionnée
                    resized_img.save(self.output_path)
                    self.logger.debug(f"L'image a été redimensionnée ({ratio}) et sauvegardée sous : {self.output_path}")
                    return True
        except Exception as e:
            self.logger.error(f"Une erreur s'est produite : {e}") 
            return False
 
