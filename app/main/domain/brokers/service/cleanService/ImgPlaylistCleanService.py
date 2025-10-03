
import os
from django.core.files.storage import default_storage
from main.architecture.persistence.models.Playlist import Playlist
from main.domain.common.exceptions.FileManagementException import FileNotInDatabase, FileNoteFound
from main.domain.brokers.service.cleanService.BaseCleanService import BaseCleanService
from main.domain.common.utils.logger import LoggerFactory


class ImgPlaylistCleanService(BaseCleanService):
    def __init__(self, storage_location=None, folder=None):
        self.logger = LoggerFactory.get_default_logger()
        self.storage_location = storage_location or default_storage.location
        self.folder = folder or Playlist.PLAYLIST_FOLDER

    def file_exists_in_db(self, file_path):
        """Vérifie si un fichier existe dans la base de données."""
        return Playlist.objects.filter(icon=file_path).exists() #TODO repository

    