import logging
from django.http import HttpRequest
from home.models.Playlist import Playlist
from home.service.MusicService import MusicService

logger = logging.getLogger('home')

class MultipleMusicUploadService:
    """Service for handling multiple music uploads."""

    def __init__(self, request: HttpRequest):
        self.request = request
        self.music_service = MusicService(request)

    def process_upload(self, playlist: Playlist) -> tuple[list, list]:
        """
        Processes the upload of multiple music files.

        Args:
            playlist (Playlist): The playlist to add the music to.

        Returns:
            tuple[list, list]: A tuple containing a list of successfully uploaded music data and a list of errors.
        """
        results = []
        errors = []

        for file in self.request.FILES.values():
            try:
                print(f"Processing file: {file.name}")
                music = self.music_service.save_multiple_files_item(playlist, file)
                print(f"Processed file: {file.name}")

                if music:
                    results.append({
                        'id': music.id,
                        'filename': music.fileName,
                        'alternativeName': music.alternativeName
                    })
                else:
                    errors.append(f"Erreur lors de la sauvegarde de {file.name}")
            except Exception as e:
                logger.error(f"Erreur lors de l'upload de {file.name}: {str(e)}")
                errors.append(f"Erreur interne avec {file.name}")
        
        return results, errors
