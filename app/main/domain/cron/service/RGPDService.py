
from datetime import datetime, timedelta
from django.utils import timezone
from main.domain.common.email.UserMail import UserMail
from main.domain.common.service.ConfirmationUserService import ConfirmationUserService
from main.domain.common.utils.url import get_full_url
from main.domain.common.utils.logger import LoggerFactory

from main.domain.common.repository.UserRepository import UserRepository



class RGPDService:
    def __init__(self):
        self.logger = LoggerFactory.get_default_logger()
        
    def prevent_inactive_users(self):
        # Obtenir la date de 22 mois avant aujourd'hui
        cutoff_date = self._calculate_cuttoff_date(22)

        # Récupérer tous les utilisateurs qui ont une dernière connexion avant la date de coupure
        inactive_users = UserRepository().get_inactive_users(cutoff_date)
        for user in inactive_users:
            self.logger.info(f"Utilisateur {user.username} alert for suppression.")
            UserMail(user).prevent_account_deletion()
        return self

    def delete_inactive_users(self):
        # Obtenir la date de 24 mois avant aujourd'hui
        cutoff_date = self._calculate_cuttoff_date(24)

        # Récupérer tous les utilisateurs qui ont une dernière connexion avant la date de coupure
        inactive_users = UserRepository().get_inactive_users(cutoff_date)
        for user in inactive_users:
            user.delete()
            self.logger.info(f"Utilisateur {user.username} supprimé.") 
            UserMail(user).account_auto_deletion()
        return self
            
    def delete_not_active_users(self):
        # Obtenir la date de 6 mois avant aujourd'hui
        cutoff_date = self._calculate_cuttoff_date(6)

        # Récupérer tous les utilisateurs qui ont une derniere connexion avant la date de coupure
        inactive_users = UserRepository().get_not_actived_users(cutoff_date)
        
        for user in inactive_users:
            user.delete()
            self.logger.info(f"Utilisateur {user.username} supprimé.")
            UserMail(user).account_auto_deletion_never_login()
        return self
    
    def prevent_not_confirmed(self):
        # Obtenir la date de 6 mois avant aujourd'hui
        cutoff_date = self._calculate_cuttoff_date(1)

        # Récupérer tous les utilisateurs qui ont une derniere connexion avant la date de coupure
        not_confirmed_users = UserRepository().get_not_confirmed_users(cutoff_date)
        for user in not_confirmed_users:
            url =  get_full_url(ConfirmationUserService(user).generation_uri(False))
            self.logger.info(f"Utilisateur {user.username} alert for suppression not confirmed.")
            UserMail(user).prevent_account_auto_deletion_never_confirmed(url)
            
    def delete_not_confirmed(self):
        # Obtenir la date de 6 mois avant aujourd'hui
        cutoff_date = self._calculate_cuttoff_date(2)

        # Récupérer tous les utilisateurs qui ont une derniere connexion avant la date de coupure
        not_confirmed_users = UserRepository().get_not_confirmed_users(cutoff_date)
        for user in not_confirmed_users:
            user.delete()
            self.logger.info(f"Utilisateur {user.username} supprimé.")
            UserMail(user).account_auto_deletion_never_confirmed()
            
    def _calculate_cuttoff_date(self, nb_month:int):
        # Obtenir la date de X mois avant aujourd'hui
        
        cutoff_date = timezone.now() - timedelta(days=nb_month*30)
        return cutoff_date
            

