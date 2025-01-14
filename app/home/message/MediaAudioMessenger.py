import logging
from celery import shared_task
from home.service.AudioCleanService import AudioCleanService

@shared_task
def clean_audio_messenger(list_media_file:list):
    logger = logging.getLogger(__name__)
    logger.info("clean_audio_messenger STARTED")
    logger.debug(f"Received list_media_file: {list_media_file}")
    (AudioCleanService()).clean_audio_files(list_media_file)
    logger.info("clean_audio_messenger ENDED")
    return True