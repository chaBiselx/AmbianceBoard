from main.architecture.persistence.repository.TrackLabelRepository import TrackLabelRepository
from main.domain.common.utils.settings import Settings
from main.domain.common.utils.logger import LoggerFactory
from main.domain.brokers.message.MusicLabelerMessenger import analyze_music_task



class MusicLabelerCronService:
    """
    Service cron qui identifie les tracks non labélisées
    et dispatche leur analyse via Celery/RabbitMQ.
    """

    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()
        self.repository = TrackLabelRepository()
        self.batch_size = Settings.get("MUSIC_LABELER_BATCH_SIZE", 50)

    def dispatch_unlabeled_tracks(self) -> int:
        """
        Trouve les musiques sans labels et dispatche une tâche Celery par music_id.
        Les tâches sont étalées avec un délai progressif pour éviter un pic de charge.

        Returns:
            int: Nombre de tâches dispatchées.
        """
        DELAY_BETWEEN_TASKS = 2  # secondes entre chaque tâche

        music_ids = self.repository.get_unlabeled_music_ids(limit=self.batch_size)

        for i, music_id in enumerate(music_ids):
            analyze_music_task.apply_async(args=[music_id], priority=9, countdown=i * DELAY_BETWEEN_TASKS)

        self.logger.info(f"MusicLabelerCron: {len(music_ids)} tâches dispatchées (étalées sur ~{len(music_ids) * DELAY_BETWEEN_TASKS}s)")
        return len(music_ids)
