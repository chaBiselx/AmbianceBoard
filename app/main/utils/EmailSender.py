import smtplib
from main.utils.logger import LoggerFactory
from parameters import settings
from email.message import EmailMessage
from typing import List, Optional
from main.exceptions.EmailException import DebugModeActivedWitoutDebugMailException, AttachementException, SendException
from email.mime.text import MIMEText

class EmailSender:
    def __init__(
            self, 
            smtp_server: str = settings.EMAIL_SMTP_SERVEUR, 
            smtp_port: int = settings.EMAIL_SMTP_PORT, 
            username: str = settings.EMAIL_SMTP_USERNAME, 
            password: str = settings.EMAIL_SMTP_PASSWORD,
            use_tls: bool = settings.EMAIL_SMTP_PASSWORD
        ):
        """
        Initialise l'EmailSender.
        
        :param smtp_server: Adresse du serveur SMTP.
        :param smtp_port: Port du serveur SMTP.
        :param username: Nom d'utilisateur pour l'authentification SMTP.
        :param password: Mot de passe pour l'authentification SMTP.
        :param debug_mode: Si True, redirige les emails vers debug_email.
        :param debug_email: Adresse email utilisée en mode debug.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.logger = LoggerFactory.get_default_logger('mail')

    def send_email(self, subject: str, body: str, from_email: str, to_emails: List[str], attachments: Optional[List[str]] = None):
        """
        Envoie un email avec les paramètres fournis.
        
        :param subject: Sujet de l'email.
        :param body: Contenu de l'email.
        :param from_email: Adresse email de l'expéditeur.
        :param to_emails: Liste des adresses des destinataires.
        :param attachments: Liste des chemins vers les fichiers à joindre.
        """

        # Crée le message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_emails
        msg.set_content(body)

        # Ajoute les pièces jointes
        if attachments:
            for file_path in attachments:
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        file_name = file_path.split("/")[-1]
                        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
                except Exception as e:
                    raise AttachementException(f"{file_path}: {e}")

        # Envoie l'email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if(self.use_tls) :
                    server.starttls()  # Active la connexion sécurisée
                server.login(self.username, self.password)
                self.logger.info(f"Email envoyé de {msg['From']} à {msg['To']} : {msg['Subject']}")
                server.send_message(msg)
                return True
        except Exception as e:
            self.logger.error(e)
            raise SendException(f"{e}")
        
