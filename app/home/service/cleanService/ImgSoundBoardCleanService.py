import logging
import os
from django.core.files.storage import default_storage
from home.models.SoundBoard import SoundBoard
from home.exceptions.FileManagementException import FileNotInDatabase, FileNoteFound
from home.service.cleanService.BaseCleanService import BaseCleanService



class ImgSoundboardCleanService(BaseCleanService):
    def __init__(self, storage_location=None, folder=None):
        self.logger = logging.getLogger('home')
        self.storage_location = storage_location or default_storage.location
        self.folder = folder or Soundboard.SOUNDBOARD_FOLDER

    def file_exists_in_db(self, file_path):
        """Vérifie si un fichier existe dans la base de données."""
        return Soundboard.objects.filter(icon=file_path).exists()

    