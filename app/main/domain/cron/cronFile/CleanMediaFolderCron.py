from main.domain.cron.service.MediaAudioService import MediaAudioService
from main.domain.cron.service.MediaImgPlaylistService import MediaImgPlaylistService
from main.domain.cron.service.MediaImgSoundboardService import MediaImgSoundboardService
from main.utils.logger import logger


def run():
    # code de votre tâche cron
    logger.info("Starting ClearMediaFolderCron")
    (MediaAudioService()).clear_media_audio()
    (MediaImgPlaylistService()).clear_media_img()
    (MediaImgSoundboardService()).clear_media_img()
    logger.info("Ending ClearMediaFolderCron")