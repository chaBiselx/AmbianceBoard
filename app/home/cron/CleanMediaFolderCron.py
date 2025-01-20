import logging
from home.service.MediaAudioService import MediaAudioService
from home.service.MediaImgPlaylistService import MediaImgPlaylistService
from home.service.MediaImgSoundboardService import MediaImgSoundboardService


def run():
    # code de votre tâche cron
    logger = logging.getLogger(__name__)
    logger.info("Starting ClearMediaFolderCron")
    (MediaAudioService()).clear_media_audio()
    (MediaImgPlaylistService()).clear_media_img()
    (MediaImgSoundboardService()).clear_media_img()
    logger.info("Ending ClearMediaFolderCron")