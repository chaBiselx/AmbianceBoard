import logging
from datetime import datetime, timedelta
from home.models.User import User
from django.utils import timezone
from home.email.UserMail import UserMail

class RGPDService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def prevent_inactive_users(self):
        # Obtenir la date de 22 mois avant aujourd'hui
        cutoff_date = self._calculate_cuttoff_date(22)

        # Récupérer tous les utilisateurs qui ont une dernière connexion avant la date de coupure
        inactive_users = User.objects.filter(last_login__lte=cutoff_date)
        for user in inactive_users:
            self.logger.info(f"Utilisateur {user.username} alert for suppression.")
            UserMail(user).prevent_account_deletion()
        return self

    def delete_inactive_users(self):
        # Obtenir la date de 24 mois avant aujourd'hui
        cutoff_date = self._calculate_cuttoff_date(24)

        # Récupérer tous les utilisateurs qui ont une dernière connexion avant la date de coupure
        inactive_users = User.objects.filter(last_login__lte=cutoff_date)
        for user in inactive_users:
            user.delete()
            self.logger.info(f"Utilisateur {user.username} supprimé.")
            UserMail(user).account_auto_deletion()
        return self
            
    def delete_not_active_users(self):
        # Obtenir la date de 6 mois avant aujourd'hui
        cutoff_date = self._calculate_cuttoff_date(6)

        # Récupérer tous les utilisateurs qui ont une derniere connexion avant la date de coupure
        inactive_users = User.objects.filter(last_login=None, date_joined__lte=cutoff_date)
        
        for user in inactive_users:
            user.delete()
            self.logger.info(f"Utilisateur {user.username} supprimé.")
            UserMail(user).account_auto_deletion_never_login()
        return self
            
    def _calculate_cuttoff_date(self, nb_month:int):
        # Obtenir la date de X mois avant aujourd'hui
        cutoff_date = timezone.now() - timedelta(days=nb_month*30)
        return cutoff_date
            

