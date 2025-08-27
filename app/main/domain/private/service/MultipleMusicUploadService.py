
from django.http import HttpRequest
from main.architecture.persistence.models.Playlist import Playlist
from main.service.MusicService import MusicService

from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper

from main.domain.common.utils.logger import logger

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
                music = self.music_service.save_multiple_files_item(playlist, file)

                if music:
                    results.append({
                        'id': music.id,
                        'filename': music.fileName,
                        'alternativeName': music.alternativeName
                    })
                    ActivityContextHelper.set_action(self.request, activity_type=UserActivityTypeEnum.MUSIC_UPLOAD, user=self.request.user, content_object=music)
                else:
                    errors.append(f"Erreur lors de la sauvegarde de {file.name}")
            except Exception as e:
                logger.error(f"Erreur lors de l'upload de {file.name}: {str(e)}")
                errors.append(f"Erreur interne avec {file.name}")
        
        return results, errors
