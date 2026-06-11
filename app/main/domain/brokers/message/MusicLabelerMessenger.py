from celery import shared_task
from main.domain.common.utils.logger import logger


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def analyze_music_task(self, music_id: int):
    """
    Tâche Celery unitaire : analyse une seule musique via le microservice music-labeler.
    Dispatché par le cron, acheminé par RabbitMQ.
    """
    from main.domain.common.service.MusicLabelerService import MusicLabelerService
    logger.info(f"MusicLabelerMessenger: start analysis for music_id={music_id}")

    service = MusicLabelerService()

    try:
        service.analyze_by_id(music_id)
        logger.info(f"MusicLabelerMessenger: music_id={music_id} analysée avec succès")
    except FileNotFoundError:
        logger.warning(f"MusicLabelerMessenger: fichier introuvable pour music_id={music_id}")
    except (ConnectionError, TimeoutError) as e:
        logger.warning(f"MusicLabelerMessenger: erreur réseau pour music_id={music_id}: {e}, retry...")
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f"MusicLabelerMessenger: erreur pour music_id={music_id}: {e}")
