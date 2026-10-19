from main.domain.common.utils.logger import logger
from main.domain.cron.service.MediaFileStructureService import MediaFileStructureService


def run():
    logger.info("Starting media file structure check")
    MediaFileStructureService().normalize_music_files()
    logger.info("Finished media file structure check")
