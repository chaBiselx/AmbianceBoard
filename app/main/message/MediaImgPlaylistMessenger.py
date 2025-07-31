from celery import shared_task
from main.service.cleanService.ImgPlaylistCleanService import ImgPlaylistCleanService
from main.utils.logger import logger

@shared_task
def clean_img_files(list_media_file:list):
    logger.info("clean_audio_messenger STARTED")
    logger.debug(f"Received list_media_file: {list_media_file}")
    (ImgPlaylistCleanService()).clean_files(list_media_file)
    logger.info("clean_audio_messenger ENDED")
    return True