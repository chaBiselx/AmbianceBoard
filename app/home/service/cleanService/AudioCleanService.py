import logging
import os
from django.core.files.storage import default_storage
from home.models.Music import Music
from home.exceptions.FileManagementException import FileNotInDatabase, FileNoteFound
from home.service.cleanService.BaseCleanService import BaseCleanService


class AudioCleanService(BaseCleanService):
    def __init__(self, storage_location=None, folder=None):
        self.logger = logging.getLogger(__name__)
        self.storage_location = storage_location or default_storage.location
        self.folder = folder or Music.MUSIC_FOLDER

    def file_exists_in_db(self, file_path):
        """Vérifie si un fichier existe dans la base de données."""
        return Music.objects.filter(file=file_path).exists()

