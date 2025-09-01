from celery import shared_task
from main.domain.brokers.service.cleanService.ImgPlaylistCleanService import ImgPlaylistCleanService
from main.domain.common.utils.logger import logger

@shared_task
def clean_img_files(list_media_file:list):
    logger.info("clean_img_soundboard_files STARTED")
    logger.debug(f"Received list_media_file: {list_media_file}")
    (ImgPlaylistCleanService()).clean_files(list_media_file)
    logger.info("clean_img_files for soundboard images ENDED")
    return True