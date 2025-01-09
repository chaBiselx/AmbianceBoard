import logging
import os
from celery import shared_task
from django.core.files.storage import default_storage
from home.models.Music import Music

@shared_task
def clean_audio_messenger(list_media_file:list):
    logger = logging.getLogger(__name__)
    for media_file in list_media_file:
        try:
            file_path = Music.MUSIC_FOLDER + media_file
            music_record = Music.objects.filter(file=file_path)
            if not music_record.exists():
                raise Exception("File not found in the database")
            logger.debug(f"File in database: Keep {media_file}")
        except Exception:
            logger.debug(f"File not in database: Deleting {media_file}")
            os.remove(default_storage.location + "/" + Music.MUSIC_FOLDER + media_file)
        
    return True