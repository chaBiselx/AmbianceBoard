from abc import ABC, abstractmethod
from home.utils.ImageResizer import ImageResizer
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
import os


class ReduceSizeImgStrategyBase():
    def __init__(self):
        self.logger = logging.getLogger('home')
    
    @abstractmethod
    def resize(self, model):
        pass
    
    def is_new_file(self, image_output_path, path):
        return image_output_path and image_output_path != path
    
    def replace_file_storage(self, original_path, image_output_path):
        # Delete the old file if it's different from the new one
        if default_storage.exists(original_path) and original_path != image_output_path:
            default_storage.delete(original_path)
        
        # Delete the temporary resized file created by ImageResizer
        if os.path.exists(image_output_path):
            os.remove(image_output_path)
            
    def get_content_file(self, image_output_path):
        with open(image_output_path, 'rb') as f:
            return ContentFile(f.read())

    def _update_model_with_new_image(self, image_field, image_output_path):
        original_path = image_field.path
        image_content = self.get_content_file(image_output_path)
        new_filename = os.path.basename(image_output_path)
        
        # Use image_field.save to let Django handle file saving correctly
        image_field.save(new_filename, image_content, save=False)
        self.replace_file_storage(original_path, image_output_path)
    

class PlaylistReduceSizeImgStrategy(ReduceSizeImgStrategyBase):
    def resize(self, model):
        if hasattr(model, 'icon') and model.icon and hasattr(model.icon, 'path') and model.icon.path:
            image_output_path = ImageResizer(model.icon.path, model.icon.path).resize_image()
            if self.is_new_file(image_output_path, model.icon.path):
                self._update_model_with_new_image(model.icon, image_output_path)
                model.update()
        else:
            self.logger.warning(f"Playlist model {model.name} has no icon to resize.")


class SoundBoardReduceSizeImgStrategy(ReduceSizeImgStrategyBase):
    def resize(self, model):
        if hasattr(model, 'icon') and model.icon and hasattr(model.icon, 'path') and model.icon.path:
            image_output_path = ImageResizer(model.icon.path, model.icon.path).resize_image()

            if self.is_new_file(image_output_path, model.icon.path):
                self._update_model_with_new_image(model.icon, image_output_path)
                model.update()
        else:
            self.logger.warning(f"SoundBoard model {model.name} has no icon to resize.")


class ReduceSizeImgStrategy:
    def __init__(self):
        from home.models.Playlist import Playlist
        from home.models.SoundBoard import SoundBoard
        self._strategies = {
            Playlist.__name__: PlaylistReduceSizeImgStrategy(),
            SoundBoard.__name__: SoundBoardReduceSizeImgStrategy(),
        }

    def get_strategy(self, model_name: str) -> ReduceSizeImgStrategyBase | None:
        return self._strategies.get(model_name)
