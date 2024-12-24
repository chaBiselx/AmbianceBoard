import logging
from ..service.MediaAudioService import MediaAudioService


def run():
    # code de votre tâche cron
    logger = logging.getLogger(__name__)
    logger.info("Starting ClearMediaFolderCron")
    (MediaAudioService()).clear_media_audio()
    logger.info("Ending ClearMediaFolderCron")