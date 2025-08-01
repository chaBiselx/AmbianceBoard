from main.utils.logger.ILogger import ILogger
from django.template.loader import render_to_string
from django.conf import settings
from main.models.ReportContent import ReportContent
from main.utils.EmailSender import EmailSender
from main.utils.logger import LoggerFactory


class ModeratorEmail():
    def __init__(self) -> None:
        self.logger: ILogger = LoggerFactory.get_default_logger()
        self.from_email: str = settings.EMAIL_NO_REPLAY
        self.to_emails: list[str] = settings.EMAILS_LISTING_MODERATORS

    def report_content_reported(self, report: ReportContent) -> None:
        """
        Send an email to the moderator when content is reported.
        
        :param user: The user who created the content.
        :param report: The report details.
        """
        if not self._has_moderator_email():
            self.logger.error("No moderator email configured.")
            return
        
        subject = 'Contenu signalé'
        html_content = render_to_string('EmailTemplate/moderator/contentReported.html', {
            'title': "Contenu signalé",
            'report': report
        })
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, self.to_emails)
            self.logger.info(f"Email de signalement envoyé à {self.to_emails}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de signalement à {self.to_emails}: {e}")
            
    def _has_moderator_email(self) -> bool:
        """
        Check if the moderator email is configured.
        
        :return: True if the moderator email is configured, False otherwise.
        """
        return bool(self.to_emails) and len(self.to_emails) > 0 and self.from_email