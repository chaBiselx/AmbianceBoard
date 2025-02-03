import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from home.utils.EmailSender import EmailSender


class UserMail:
    def __init__(self, user):
        self.logger = logging.getLogger(__name__)
        self.user = user
    def send_welcome_email(self):
        """
        Sends a welcome email to the user using a predefined HTML template.

        The email's subject is 'Bienvenue sur notre site' and is sent from 'noreply@votresite.com'. 
        The recipient is the user's email address. The HTML content is rendered from the 
        'EmailTemplate/welcomEmail.html' template and a plain text version is created by stripping 
        the HTML tags.

        If the email is sent successfully, an info log is recorded. Otherwise, an error log is 
        generated if an exception occurs.

        Raises:
            Exception: An error occurred while sending the email.
        """
        subject = 'Bienvenue sur notre site'
        from_email = 'noreply@votresite.com'
        to = self.user.email
        
        self.logger.debug(f"Email de bienvenue envoyé à {to}")
        

        # Rendre le template HTML
        html_content = render_to_string('EmailTemplate/welcomEmail.html', {'title': "Bienvenue" ,'user': self.user})
        # Créer la version texte
        # text_content = strip_tags(html_content) # ou render_to_string('emails/welcome_email.txt', {'user': self.user})
        
        try:
            mailer = EmailSender()
            mailer.send_email(subject, html_content, from_email, [to])
            self.logger.info(f"Email de bienvenue envoyé à {to}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email de bienvenue à {to}: {e}")
            
