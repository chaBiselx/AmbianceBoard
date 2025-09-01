from typing import List, Optional
from main.architecture.persistence.models.GeneralNotification import GeneralNotification
from main.architecture.persistence.models.UserNotificationDismissal import UserNotificationDismissal
from main.architecture.persistence.models.User import User
from main.domain.common.repository.GeneralNotificationRepository import GeneralNotificationRepository

class GeneralNotificationService:
    """
    Service pour la gestion des notifications générales.
    
    Fournit des méthodes pour récupérer et gérer les notifications
    en fonction du statut d'authentification des utilisateurs.
    """

    def __init__(self, user: User|None = None):
        self.user = user
        self.general_notification_repository = GeneralNotificationRepository()
        
    def get_list_notifications(self) -> List[GeneralNotification]:
        """
        Récupère toutes les notifications actives disponibles pour l'utilisateur.
        
        Returns:
            List[GeneralNotification]: Liste des notifications actives
        """
        return self.general_notification_repository.get_list_notifications_actives(self.user)

        