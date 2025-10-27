"""
Service pour gérer l'expiration des abonnements utilisateur
"""
from django.utils import timezone
from main.domain.common.utils.settings import Settings

from main.architecture.persistence.models.UserTier import UserTier
from main.domain.common.utils.logger import logger
from main.domain.common.email.UserMail import UserMail
from main.architecture.persistence.repository.UserTiersRepository import UserTiersRepository




class UserTierExpirationService:
    """
    Service pour gérer la logique d'expiration des tiers d'utilisateurs.
    """
    def __init__(self):
        self.delta_days = Settings.get('TIER_EXPIRATION_WARNING_DAYS')  # Nombre de jours avant l'expiration pour envoyer un avertissement

    def handle_expired_tiers(self):
        """
        Gère les tiers qui ont expiré.
        """
        logger.info("Début de la gestion des tiers expirés.")
        expired_count = 0
        try:
            expired_tiers = UserTiersRepository().get_expired_user_premium_tiers()

            for user_tier in expired_tiers:
                try:
                    logger.info(f"Expiration du tier {user_tier.tier_name} pour l'utilisateur {user_tier.user.username}")
                    user_tier.downgrade_to_standard()
                    expired_count += 1
                    self._send_expiration_notification(user_tier.user, user_tier)
                except Exception as e:
                    logger.error(f"Erreur lors de l'expiration du tier pour {user_tier.user.username}: {str(e)}")
            
            logger.info(f"Gestion des tiers expirés terminée: {expired_count} tier(s) rétrogradé(s).")
        except Exception as e:
            logger.error(f"Erreur lors de la gestion des expirations de tiers: {str(e)}")
        return expired_count

    def send_expiration_warnings(self):
        """
        Envoie des avertissements pour les tiers qui expireront bientôt.
        """
        logger.info("Début de l'envoi des avertissements d'expiration.")
        warning_count = 0
        try:
            upcoming_expirations = UserTiersRepository().get_upcoming_expirations_user_tiers(self.delta_days)
            for user_tier in upcoming_expirations:
                try:
                    days_left = (user_tier.tier_expiry_date - timezone.now()).days
                    logger.info(f"Notification d'expiration dans {days_left} jours pour {user_tier.user.username}")
                    self._send_expiration_warning(user_tier.user, days_left)
                    warning_count += 1
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de l'avertissement pour {user_tier.user.username}: {str(e)}")

            logger.info(f"Envoi des avertissements d'expiration terminé: {warning_count} avertissement(s) envoyé(s).")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des avertissements d'expiration: {str(e)}")
        return warning_count

    def _send_expiration_notification(self, user, user_tier):
        """Envoie un email de notification d'expiration"""
        user_mail = UserMail(user)
        user_mail.tiers_downgrade_notification(user_tier.tier_name)
        
        
    def _send_expiration_warning(self, user, days_left):
        """Envoie un email d'avertissement d'expiration prochaine"""
        user_mail = UserMail(user)
        user_mail.tiers_expiration_warning(days_left)
