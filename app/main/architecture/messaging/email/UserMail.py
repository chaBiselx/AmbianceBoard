from main.domain.common.utils.logger.ILogger import ILogger
from main.domain.common.utils.settings import Settings
from django.utils.translation import get_language, gettext as _, override
from django.template.loader import render_to_string
from django.urls import reverse
from main.architecture.persistence.models.User import User
from main.domain.common.utils.EmailSender import EmailSender
from main.domain.common.utils.logger import LoggerFactory
from main.domain.common.utils.url import get_full_url


class UserMail:
    def __init__(self, user: User) -> None:
        self.logger: ILogger = LoggerFactory.get_default_logger()
        self.from_email: str = Settings.get('EMAIL_NO_REPLY')
        self.user: User = user

    def _render_email_template(self, template_name: str, context: dict) -> str:
        language = get_language() or 'fr'
        with override(language):
            return render_to_string(template_name, context)
        
    def send_welcome_email(self) -> None:
        """
        Sends a welcome email to the user using a predefined HTML template.

        The email's subject is 'Bienvenue sur notre site'
        The recipient is the user's email address.
        """
        subject = _('template.email.user.welcome.subject')
        html_content = self._render_email_template(
            'EmailTemplate/user/welcomEmail.html',
            {'title': _('template.email.user.welcome.subject'), 'user': self.user},
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de bienvenue envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de bienvenue à {self.user.email}: {e}")
            
    def send_account_confirmation_email(self, url: str) -> None:
        """
        Sends a welcome email to the user using a predefined HTML template.
        
        """
        subject = _('template.email.user.confirm.subject')
      
        html_content = self._render_email_template(
            'EmailTemplate/user/confirmEmail.html',
            {'title': _('template.email.user.confirm.subject'), 'user': self.user, 'url': url},
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de confirmation envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de confirmation à {self.user.email}: {e}")


    def send_reset_password_email(self, url: str) -> None:
        """
        Sends an email to send a link to reset account
        
        """
        subject = _('template.email.user.reset_password.subject')
      
        html_content = self._render_email_template(
            'EmailTemplate/user/resetPassword.html',
            {'title': _('template.email.user.reset_password.subject'), 'user': self.user, 'url': url},
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de reinitialisation envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de reinitialisation à {self.user.email}: {e}")
            
    def send_password_changed_email(self) -> None:
        """
        Sends an email to prevent user from changing password
        
        """
        subject = _('template.email.user.password_changed.subject')
        html_content = self._render_email_template(
            'EmailTemplate/user/password_changed.html',
            {'title': _('template.email.user.password_changed.subject'), 'user': self.user},
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de modification de mot de passe envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de modification de mot de passe à {self.user.email}: {e}")
            
    def account_auto_deletion(self) -> None:
        """
        Sends an account deletion email to the user using a predefined HTML template.

        The email's subject is 'Votre compte a été supprimé'
        The recipient is the user's email address.
        """
        subject = _('template.email.user.account_deleted.subject')
        html_content = self._render_email_template(
            'EmailTemplate/user/autoDeletionAccount.html',
            {'title': _('template.email.user.account_deleted.subject'), 'user': self.user},
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de suppression automatique envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de suppression  à {self.user.email}: {e}")
            
    def account_auto_deletion_never_login(self) -> None:
        """
        Sends an account deletion email to the user using a predefined HTML template.

        The email's subject is 'Votre compte a été supprimé'
        The recipient is the user's email address.
        """
        subject = _('template.email.user.account_deleted.subject')
        
        html_content = self._render_email_template(
            'EmailTemplate/user/autoDeletionAccountNeverLogin.html',
            {'title': _('template.email.user.account_deleted.subject'), 'user': self.user},
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de suppression automatique aucune connexion envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de suppression aucune connexion  à {self.user.email}: {e}")
            
    def prevent_account_deletion(self):
        """
        Sends an account deletion email to the user using a predefined HTML template.

        The email's subject is 'votre compte est inactif'
        The recipient is the user's email address.
        """
        subject = _('template.email.user.prevent_deletion.subject')
        
        html_content = self._render_email_template(
            'EmailTemplate/user/preventAutoDeletion.html',
            {'title': _('template.email.user.prevent_deletion.subject'), 'user': self.user},
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de prevention de suppression envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de prevention de suppression à {self.user.email}: {e}")
            
    def prevent_account_auto_deletion_never_confirmed(self, url):
        """
        Sends an account deletion email to the user using a predefined HTML template.

        The email's subject is 'votre compte est inactif'
        The recipient is the user's email address.
        """
        subject = _('template.email.user.prevent_deletion_unconfirmed.subject')
        html_content = self._render_email_template(
            'EmailTemplate/user/preventAutoDeletionNotConfirmed.html',
            {
                'title': _('template.email.user.prevent_deletion_unconfirmed.subject'),
                'user': self.user,
                'url': url,
            },
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de prevention de suppression envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de prevention de suppression à {self.user.email}: {e}")

    def account_auto_deletion_never_confirmed(self):
        """
        Sends an account deletion email to the user using a predefined HTML template.

        The email's subject is 'Votre compte a été supprimé'
        The recipient is the user's email address.
        """
        subject = _('template.email.user.account_deleted_unconfirmed.subject')
        html_content = self._render_email_template(
            'EmailTemplate/user/autoDeletionNotConfirmed.html',
            {'title': _('template.email.user.account_deleted_unconfirmed.subject'), 'user': self.user},
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de suppression automatique Aucune confirmation {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de suppression Aucune confirmation à {self.user.email}: {e}")
        

    def tiers_downgrade_notification(self, new_tier):
        """
        Sends a notification email to the user when their tier is downgraded.
        
        """
        subject = _('template.email.user.tier_downgrade.subject')
        html_content = self._render_email_template(
            'EmailTemplate/user/tierDowngradeNotification.html',
            {
                'title': _('template.email.user.tier_downgrade.subject'),
                'user': self.user,
                'new_tier': new_tier,
            },
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de notification de rétrogradation envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de notification de rétrogradation à {self.user.email}: {e}") 
            
    def playlist_proposal_received(self, playlist_proposal) -> None:
        """
        Sends an email to the soundboard owner when a playlist proposal is received.

        """
        subject = _('template.email.user.playlist_proposal_received.subject')
        manage_url = get_full_url(reverse('playlistProposalsList'))
        html_content = self._render_email_template(
            'EmailTemplate/user/playlistProposalReceived.html',
            {
                'title': _('template.email.user.playlist_proposal_received.subject'),
                'user': self.user,
                'proposal': playlist_proposal,
                'manage_url': manage_url,
            },
        )

        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de proposition de playlist envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de proposition de playlist à {self.user.email}: {e}")

    def tiers_expiration_warning(self, days_left):
        """
        Sends a warning email to the user when their tier is about to expire.
        
        """
        subject = _('template.email.user.tier_expiration.subject')
        html_content = self._render_email_template(
            'EmailTemplate/user/tierExpirationWarning.html',
            {
                'title': _('template.email.user.tier_expiration.subject'),
                'user': self.user,
                'days_left': days_left,
            },
        )
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email d'avertissement d'expiration envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email d'avertissement d'expiration à {self.user.email}: {e}")
                   
