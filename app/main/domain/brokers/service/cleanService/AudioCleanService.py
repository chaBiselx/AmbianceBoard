
import os
from django.core.files.storage import default_storage
from main.architecture.persistence.models.Music import Music
from main.domain.common.exceptions.FileManagementException import FileNotInDatabase, FileNoteFound
from main.domain.brokers.service.cleanService.BaseCleanService import BaseCleanService
from main.domain.common.utils.logger import LoggerFactory
from main.architecture.persistence.repository.MusicRepository import MusicRepository

class AudioCleanService(BaseCleanService):
    def __init__(self, storage_location=None, folder=None):
        self.logger = LoggerFactory.get_default_logger()
        self.storage_location = storage_location or default_storage.location
        self.folder = folder or Music.MUSIC_FOLDER
        self.music_repository = MusicRepository()

    def file_exists_in_db(self, file_path):
        """Vérifie si un fichier existe dans la base de données."""
        return self.music_repository.exist_from_path(file_path)

