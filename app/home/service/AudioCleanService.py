import logging
import os
from django.core.files.storage import default_storage
from home.models.Music import Music
from home.exceptions.FileManagementException import FileNotInDatabase


class AudioCleanService:
    def __init__(self, storage_location=None, music_folder=None):
        self.logger = logging.getLogger(__name__)
        self.storage_location = storage_location or default_storage.location
        self.music_folder = music_folder or Music.MUSIC_FOLDER

    def file_exists_in_db(self, file_path):
        """Vérifie si un fichier existe dans la base de données."""
        return Music.objects.filter(file=file_path).exists()

    def delete_file(self, file_path):
        """Supprime un fichier du système de fichiers."""
        os.remove(file_path)

    def clean_audio_files(self, list_media_file: list):
        """Nettoie les fichiers audio qui ne sont pas dans la base de données."""
        for media_file in list_media_file:
            file_path = self.music_folder + media_file
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