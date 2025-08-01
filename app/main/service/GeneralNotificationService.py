from typing import List, Optional
from main.models.GeneralNotification import GeneralNotification
from main.models.UserNotificationDismissal import UserNotificationDismissal
from main.models.User import User
from main.filters.GeneralNotificationFilter import GeneralNotificationFilter


class GeneralNotificationService:
    """
    Service pour la gestion des notifications générales.
    
    Fournit des méthodes pour récupérer et gérer les notifications
    en fonction du statut d'authentification des utilisateurs.
    """

    def __init__(self, user: User|None = None):
        self.user = user
        
    def get_list_notifications(self) -> List[GeneralNotification]:
        """
        Récupère toutes les notifications actives disponibles pour l'utilisateur.
        
        Returns:
            List[GeneralNotification]: Liste des notifications actives
        """
        general_notification_filter = GeneralNotificationFilter()
        general_notification_filter.filter_by_active(True)
        general_notification_filter.filter_by_date()
        if self.user is not None and self.user.is_authenticated:
            general_notification_filter.filter_by_user_has_notifications(self.user)
        else :
            general_notification_filter.filter_by_for_authenticated_users(False)
        return general_notification_filter.queryset.order_by('-start_date')
        