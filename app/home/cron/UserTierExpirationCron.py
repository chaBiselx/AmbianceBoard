import logging

from home.service.cron.UserTierExpirationService import UserTierExpirationService

logger = logging.getLogger('home')

def run():
    logger.info("Début de la vérification des expirations de tiers utilisateur via le service.")
    
    try:
        user_tier_expiration_service = UserTierExpirationService()
        user_tier_expiration_service.handle_expired_tiers()
        user_tier_expiration_service.send_expiration_warnings()

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du cron d'expiration des tiers: {str(e)}")
    
    logger.info("Fin de la vérification des expirations de tiers utilisateur via le service.")

