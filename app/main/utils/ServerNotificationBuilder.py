from django.contrib import messages
from django.utils.safestring import mark_safe






class ServerNotificationBuilder:
    statut : str = "info"
    message: str = ""
    meta: dict = {}
    
    def __init__(self, request):
        """
        Initialise le constructeur de notification.
        
        Args:
            request: L'objet request de Django, si disponible.
        """
        self.request = request

    def set_message(self, message: str):
        """
        Définit le message de la notification.
        """
        self.message = message
        return self

    def set_statut(self, statut: str):
        """
        Définit le statut de la notification.

        """
        self.statut = statut
        return self

    def set_meta(self, meta: dict):
        """
        Définit les métadonnées de la notification.

        Args:
            meta: Dictionnaire de métadonnées
        """
        self.meta = meta
        return self
        
    def send(self) -> None:
        """
        Envoie la notification au client via le système de messages de Django.
        
        Args:
            request: L'objet request de Django
        """
        if self.statut == "info":
            messages.info(self.request, mark_safe(self.message), )
        elif self.statut == "success":
            messages.success(self.request, mark_safe(self.message))
        elif self.statut == "warning":
            messages.warning(self.request, mark_safe(self.message))
        elif self.statut == "error":
            messages.error(self.request, mark_safe(self.message))
        else:
            raise ValueError(f"Statut {self.statut} non reconnu pour la notification")