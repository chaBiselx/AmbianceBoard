
import os
from django.core.files.storage import default_storage
from main.models.Music import Music
from main.domain.common.exceptions.FileManagementException import FileNotInDatabase, FileNoteFound
from main.service.cleanService.BaseCleanService import BaseCleanService
from main.utils.logger import LoggerFactory

class AudioCleanService(BaseCleanService):
    def __init__(self, storage_location=None, folder=None):
        self.logger = LoggerFactory.get_default_logger()
        self.storage_location = storage_location or default_storage.location
        self.folder = folder or Music.MUSIC_FOLDER

    def file_exists_in_db(self, file_path):
        """Vérifie si un fichier existe dans la base de données."""
        return Music.objects.filter(file=file_path).exists()

