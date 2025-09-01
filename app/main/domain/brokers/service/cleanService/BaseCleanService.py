
import os
from django.core.files.storage import default_storage
from main.architecture.persistence.models.Music import Music
from main.domain.common.exceptions.FileManagementException import FileNotInDatabase, FileNoteFound
from main.domain.common.utils.logger import LoggerFactory

class BaseCleanService:
    def __init__(self, storage_location=None, folder=None):
        self.logger = LoggerFactory.get_default_logger()
        self.storage_location = storage_location or default_storage.location
        self.folder = folder or Music.MUSIC_FOLDER

    def delete_file(self, file_path):
        """Supprime un fichier du système de fichiers."""
        os.remove(file_path)

    def clean_files(self, list_media_file: list):
        """Nettoie les fichiers qui ne sont pas dans la base de données."""
        for media_file in list_media_file:
            file_path = self.folder + media_file
            try:
                if not os.path.exists(f"{self.storage_location}/{file_path}"):
                    raise FileNoteFound("File not found on the system")
                
                if not self.file_exists_in_db(file_path):
                    raise FileNotInDatabase("File not found in the database")
                
                self.logger.debug(f"File in database: Keep {media_file}")
            except FileNotInDatabase as e:
                self.logger.debug(f"File not in database: Deleting {media_file}")
                self.delete_file(f"{self.storage_location}/{file_path}")
            except FileNoteFound as e:
                self.logger.debug(f"File not found on the system {media_file}")
            except Exception as e:
                self.logger.debug(f"Unexpected error: {e}")
        return True