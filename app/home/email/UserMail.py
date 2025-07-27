from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from home.utils.EmailSender import EmailSender
from home.utils.logger import LoggerFactory


class UserMail:
    def __init__(self, user):
        self.logger = LoggerFactory.get_default_logger()
        self.from_email = settings.EMAIL_NO_REPLAY
        self.user = user
    def send_welcome_email(self):
        """
        Sends a welcome email to the user using a predefined HTML template.

        The email's subject is 'Bienvenue sur notre site'
        The recipient is the user's email address.
        """
        subject = 'Bienvenue sur notre site'
        html_content = render_to_string('EmailTemplate/welcomEmail.html', {'title': "Bienvenue" ,'user': self.user})
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de bienvenue envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de bienvenue à {self.user.email}: {e}")
            
    def send_account_confirmation_email(self, url):
        """
        Sends a welcome email to the user using a predefined HTML template.
        
        """
        subject = 'Confirmation de votre compte'
      
        html_content = render_to_string('EmailTemplate/confirmEmail.html', {'title': "Bienvenue" ,'user': self.user, 'url': url})
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de confirmation envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de confirmation à {self.user.email}: {e}")


    def send_reset_password_email(self, url):
        """
        Sends an email to send a link to reset account
        
        """
        subject = 'Reinitialisation de votre mot de passe'
      
        html_content = render_to_string('EmailTemplate/resetPassword.html', {'title': "Bienvenue" ,'user': self.user, 'url': url})
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de reinitialisation envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de reinitialisation à {self.user.email}: {e}")
            
    def send_password_changed_email(self):
        """
        Sends an email to prevent user from changing password
        
        """
        subject = 'Modification de mot de passe'
        html_content = render_to_string('EmailTemplate/password_changed.html', {'title': "Bienvenue" ,'user': self.user})
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de modification de mot de passe envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de modification de mot de passe à {self.user.email}: {e}")
            
    def account_auto_deletion(self):
        """
        Sends an account deletion email to the user using a predefined HTML template.

        The email's subject is 'Votre compte a été supprimé'
        The recipient is the user's email address.
        """
        subject = 'Votre compte a été supprimé'
        html_content = render_to_string('EmailTemplate/autoDeletionAccount.html', {'title': "Account deleted" ,'user': self.user})
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de suppression automatique envoyé à {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de suppression  à {self.user.email}: {e}")
            
    def account_auto_deletion_never_login(self):
        """
        Sends an account deletion email to the user using a predefined HTML template.

        The email's subject is 'Votre compte a été supprimé'
        The recipient is the user's email address.
        """
        subject = 'Votre compte a été supprimé'
        
        html_content = render_to_string('EmailTemplate/autoDeletionAccountNeverLogin.html', {'title': "Account deleted" ,'user': self.user})
        
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
        subject = 'Votre compte va être supprimé'
        
        html_content = render_to_string('EmailTemplate/preventAutoDeletion.html', {'title': "Prevent deletion account due to inactivity" ,'user': self.user})
        
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
        subject = 'Votre compte va être supprimé car non confirmé'
        html_content = render_to_string('EmailTemplate/preventAutoDeletionNotConfirmed.html', {'title': "Prevent deletion account due not confirmed" ,'user': self.user, 'url': url})
        
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
        subject = 'Votre compte a été supprimé car non confirmé'
        html_content = render_to_string('EmailTemplate/autoDeletionNotConfirmed.html', {'title': "Deletion account due not confirmed" ,'user': self.user})
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, self.from_email, [self.user.email])
            self.logger.info(f"Email de suppression automatique Aucune confirmation {self.user.email}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de suppression Aucune confirmation à {self.user.email}: {e}")
        
            
