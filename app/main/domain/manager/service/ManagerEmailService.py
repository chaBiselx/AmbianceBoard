from typing import List
from django.template.loader import render_to_string
from main.architecture.persistence.models.User import User
from main.domain.brokers.message.ManagerEmailMessenger import send_manager_email_task
from main.domain.common.utils.logger import LoggerFactory


class ManagerEmailService:
    """
    Service responsable de l'envoi d'emails en masse par les managers.

    La logique d'envoi est déléguée à une tâche Celery afin de ne pas
    bloquer la requête HTTP et de passer par RabbitMQ.
    """

    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()

    def dispatch(self, recipients: List[User], subject: str, body: str, sender: User) -> int:
        """
        Enfile une tâche d'envoi d'email pour chaque destinataire via RabbitMQ/Celery.

        :param recipients: Liste des utilisateurs destinataires.
        :param subject: Sujet du message.
        :param body: Corps du message (texte brut ou HTML).
        :param sender: Utilisateur manager à l'origine de l'envoi.
        :returns: Nombre de tâches enfilées.
        """
        html_content = render_to_string('EmailTemplate/manager/managerEmail.html', {
            'title': subject,
            'message': body,
            'sender': sender,
        })
        

        queued = 0
        for user in recipients:
            if not user.email:
                self.logger.warning(f"ManagerEmailService: utilisateur {user.username} sans email, ignoré.")
                continue
            self.logger.info(f"ManagerEmailService: envoi d'email à {user.username} — sujet: {subject}")
            send_manager_email_task.delay(user.email, subject, html_content)
            queued += 1

        self.logger.info(
            f"ManagerEmailService: {queued} email(s) enfilé(s) par {sender.username} — sujet: {subject}"
        )
        return queued
