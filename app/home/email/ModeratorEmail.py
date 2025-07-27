from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from home.utils.EmailSender import EmailSender
from home.utils.logger import LoggerFactory


class ModeratorEmail():
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()
        self.from_email = settings.EMAIL_NO_REPLAY
        self.to_emails = settings.EMAILS_LISTING_MODERATORS

    def report_content_reported(self, report):
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
            
    def _has_moderator_email(self):
        """
        Check if the moderator email is configured.
        
        :return: True if the moderator email is configured, False otherwise.
        """
        return bool(self.to_emails) and len(self.to_emails) > 0 and self.from_email