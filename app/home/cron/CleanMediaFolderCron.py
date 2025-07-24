from home.service.MediaAudioService import MediaAudioService
from home.service.MediaImgPlaylistService import MediaImgPlaylistService
from home.service.MediaImgSoundboardService import MediaImgSoundboardService
from home.utils.logger import logger


def run():
    # code de votre tâche cron
    logger.info("Starting ClearMediaFolderCron")
    (MediaAudioService()).clear_media_audio()
    (MediaImgPlaylistService()).clear_media_img()
    (MediaImgSoundboardService()).clear_media_img()
    logger.info("Ending ClearMediaFolderCron")