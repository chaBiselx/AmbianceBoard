"""
Tâche cron pour gérer l'expiration des abonnements utilisateur
"""

import logging
from django.utils import timezone
from home.models.UserTier import UserTier
from home.models.User import User


logger = logging.getLogger('home')


class UserTierExpirationCron:
    """Gère l'expiration automatique des tiers d'utilisateurs"""
    
    @staticmethod
    def run():
        """
        Exécute la vérification et la gestion des expirations de tiers
        À exécuter quotidiennement via cron
        """
        logger.info("Début de la vérification des expirations de tiers utilisateur")
        
        try:
            # Trouver tous les tiers expirés
            now = timezone.now()
            expired_tiers = UserTier.objects.filter(
                tier_expiry_date__lt=now,
                tier_name__in=['PREMIUM_BASIC', 'PREMIUM_ADVANCED', 'PREMIUM_PRO']
            )
            
            expired_count = 0
            
            for user_tier in expired_tiers:
                try:
                    logger.info(f"Expiration du tier {user_tier.tier_name} pour l'utilisateur {user_tier.user.username}")
                    
                    # Rétrogradation automatique au tier standard
                    user_tier.downgrade_to_standard()
                    expired_count += 1
                    
                    # TODO: Envoyer un email de notification à l'utilisateur
                    # UserTierExpirationCron._send_expiration_notification(user_tier.user)
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'expiration du tier pour {user_tier.user.username}: {str(e)}")
            
            logger.info(f"Expiration terminée: {expired_count} tier(s) rétrogradé(s)")
            
            # Notifications d'expiration prochaine (7 jours avant)
            UserTierExpirationCron._send_expiration_warnings()
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des expirations: {str(e)}")
    
    @staticmethod
    def _send_expiration_warnings():
        """Envoie des notifications d'expiration prochaine"""
        from datetime import timedelta
        
        now = timezone.now()
        warning_threshold = now + timedelta(days=7)
        
        upcoming_expirations = UserTier.objects.filter(
            tier_expiry_date__lte=warning_threshold,
            tier_expiry_date__gt=now,
            tier_name__in=['PREMIUM_BASIC', 'PREMIUM_ADVANCED', 'PREMIUM_PRO']
        )
        
        warning_count = 0
        
        for user_tier in upcoming_expirations:
            try:
                days_left = (user_tier.tier_expiry_date - now).days
                logger.info(f"Notification d'expiration dans {days_left} jours pour {user_tier.user.username}")
                
                # TODO: Envoyer un email d'avertissement
                # UserTierExpirationCron._send_expiration_warning(user_tier.user, days_left)
                
                warning_count += 1
                
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'avertissement pour {user_tier.user.username}: {str(e)}")
        
        logger.info(f"Avertissements d'expiration envoyés: {warning_count}")
    
    @staticmethod
    def _send_expiration_notification(user):
        """Envoie un email de notification d'expiration"""
        # TODO: Implémenter l'envoi d'email
        pass
    
    @staticmethod
    def _send_expiration_warning(user, days_left):
        """Envoie un email d'avertissement d'expiration prochaine"""
        # TODO: Implémenter l'envoi d'email d'avertissement
        pass
