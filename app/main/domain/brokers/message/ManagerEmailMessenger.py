from celery import shared_task
from main.domain.common.utils.EmailSender import EmailSender
from main.domain.common.utils.settings import Settings
from main.domain.common.utils.logger import LoggerFactory


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_manager_email_task(self, to_email: str, subject: str, html_content: str):
    """
    Tâche Celery pour l'envoi d'un email de manager à un unique destinataire.

    En cas d'échec, la tâche est relancée automatiquement (max 3 tentatives,
    délai de 60 secondes entre chaque tentative).

    :param to_email: Adresse email du destinataire.
    :param subject: Sujet du message.
    :param html_content: Corps HTML de l'email.
    """
    logger = LoggerFactory.get_default_logger('mail')

    try:
        from_email = Settings.get('EMAIL_NO_REPLY')
        mailer = EmailSender()
        mailer.send_email(subject, html_content, from_email, [to_email])
        logger.info(f"send_manager_email_task: email envoyé à {to_email} — sujet: {subject}")
        return True
    except Exception as exc:
        logger.error(f"send_manager_email_task: échec envoi à {to_email} — {exc}")
        raise self.retry(exc=exc)
