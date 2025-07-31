from main.service.MediaAudioService import MediaAudioService
from main.service.MediaImgPlaylistService import MediaImgPlaylistService
from main.service.MediaImgSoundboardService import MediaImgSoundboardService
from main.utils.logger import logger


def run():
    # code de votre tâche cron
    logger.info("Starting ClearMediaFolderCron")
    (MediaAudioService()).clear_media_audio()
    (MediaImgPlaylistService()).clear_media_img()
    (MediaImgSoundboardService()).clear_media_img()
    logger.info("Ending ClearMediaFolderCron")