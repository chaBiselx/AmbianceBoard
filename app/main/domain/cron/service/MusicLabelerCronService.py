from main.architecture.persistence.repository.MusicRepository import MusicRepository
from main.domain.common.utils.settings import Settings
from main.domain.common.utils.logger import LoggerFactory
from main.domain.brokers.message.MusicLabelerMessenger import analyze_music_task



class MusicLabelerCronService:
    """
    Service cron qui identifie les tracks non labélisées
    et dispatche leur analyse via Celery/RabbitMQ.

    Les tâches sont envoyées sur la queue dédiée 'music_labeler', traitée par
    un worker dont la concurrence est configurable via MUSIC_LABELER_CONCURRENCY
    (1 par défaut = séquentiel, sans chevauchement).
    """
    DELAY_BETWEEN_TASKS = 2  # secondes entre chaque tâche

    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()
        self.repository = MusicRepository()
        self.batch_size = Settings.get("MUSIC_LABELER_BATCH_SIZE", 1)

    def dispatch_unlabeled_tracks(self) -> int:
        """
        Trouve les musiques sans labels et enfile une tâche Celery par music_id.
        Le séquençage est garanti par le worker dédié (concurrency=1 par défaut).

        Returns:
            int: Nombre de tâches dispatchées.
        """
        music_ids = self.repository.get_unlabeled_music_ids(limit=self.batch_size)

        if not music_ids:
            self.logger.info("MusicLabelerCron: aucune musique à analyser")
            return 0

        for i, music_id in enumerate(music_ids):
            analyze_music_task.apply_async(args=[music_id], queue='music_labeler', priority=9, countdown=i * self.DELAY_BETWEEN_TASKS)

        self.logger.info(f"MusicLabelerCron: {len(music_ids)} tâche(s) enfilée(s) sur la queue music_labeler")
        return len(music_ids)
