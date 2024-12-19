import logging
from django_cron import CronJobBase, Schedule
from ..service.MediaAudioService import MediaAudioService


class CleanMediaFolder(CronJobBase):
    RUN_EVERY_MINS = 0.3 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'CleanMediaFolder'    # a unique code

    def do(self):
        # code de votre tâche cron
        logger = logging.getLogger(__name__)
        logger.info("Starting ClearMediaFolderCron")
        (MediaAudioService()).clear_media_audio()
        
        logger.info("Ending ClearMediaFolderCron")