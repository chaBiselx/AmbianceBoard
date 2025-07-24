from celery import shared_task
from home.utils.AudioBitrateReducer import AudioBitrateReducer
from home.utils.logger import logger

@shared_task
def reduce_bit_rate(path_file:str):
    logger.info("reduce_bit_rate STARTED")
    reducer = AudioBitrateReducer(path_file)
    reducer.load_audio()
    reducer.reduce_bitrate()
    logger.info("reduce_bit_rate ENDED")
    return True