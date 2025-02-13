import logging
from celery import shared_task
from home.utils.AudioBitrateReducer import AudioBitrateReducer

@shared_task
def reduce_bit_rate(path_file:str):
    logger = logging.getLogger(__name__)
    logger.info("reduce_bit_rate STARTED")
    reducer = AudioBitrateReducer(path_file)
    reducer.load_audio()
    reducer.reduce_bitrate()
    logger.info("reduce_bit_rate ENDED")
    return True