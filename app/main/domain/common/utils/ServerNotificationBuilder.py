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

    
    def add_meta(self, key: str, value):
        """
        Ajoute une métadonnée spécifique à la notification.
        
        Args:
            key: Clé de la métadonnée
            value: Valeur de la métadonnée
        """
        self.meta[key] = value
        return self
    
  
    
    def send(self) -> None:
        """
        Envoie la notification au client via le système de messages de Django.
        Les métadonnées sont passées via extra_tags sous forme de chaîne JSON.
        
        Args:
            request: L'objet request de Django
        """
        # Préparer les extra_tags avec les métadonnées
        extra_tags = ""
        if self.meta:
            import json
            try:
                # Convertir les métadonnées en JSON pour les passer via extra_tags
                meta_json = json.dumps(self.meta)
                extra_tags = f"{meta_json}"
            except (TypeError, ValueError):
                # Si la sérialisation échoue, continuer sans métadonnées
                pass
        
        if self.statut == "info":
            messages.info(self.request, mark_safe(self.message), extra_tags=extra_tags)
        elif self.statut == "success":
            messages.success(self.request, mark_safe(self.message), extra_tags=extra_tags)
        elif self.statut == "warning":
            messages.warning(self.request, mark_safe(self.message), extra_tags=extra_tags)
        elif self.statut == "error":
            messages.error(self.request, mark_safe(self.message), extra_tags=extra_tags)
        else:
            raise ValueError(f"Statut {self.statut} non reconnu pour la notification")