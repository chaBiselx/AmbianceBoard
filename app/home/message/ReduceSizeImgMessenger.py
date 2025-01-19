import logging
from celery import shared_task
from home.utils.ImageResizer import ImageResizer

@shared_task
def reduce_size_img(path_file:str):
    logger = logging.getLogger(__name__)
    logger.info("reduce_size_img STARTED")
    ImageResizer(path_file, path_file).resize_image()
    logger.info("reduce_size_img ENDED")
    return True