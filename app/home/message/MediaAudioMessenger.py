from celery import shared_task
from home.service.cleanService.AudioCleanService import AudioCleanService
from home.utils.logger import logger

@shared_task
def clean_audio_messenger(list_media_file:list):
    logger.info("clean_audio_messenger STARTED")
    logger.debug(f"Received list_media_file: {list_media_file}")
    (AudioCleanService()).clean_files(list_media_file)
    logger.info("clean_audio_messenger ENDED")
    return True