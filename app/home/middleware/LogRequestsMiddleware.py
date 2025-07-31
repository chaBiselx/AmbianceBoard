"""
Middleware pour l'enregistrement et le suivi des requêtes HTTP.

Enregistre toutes les requêtes avec des identifiants uniques
pour faciliter le débogage et le monitoring de l'application.
"""

from typing import Callable, Any, Dict
from django.http import HttpRequest, HttpResponse
import uuid
import time
import secrets
from home.utils.logger import LoggerFactory

class LogRequestsMiddleware:
    """
    Middleware pour l'enregistrement des requêtes HTTP.
    
    Enregistre toutes les requêtes avec :
    - Identifiants uniques pour les utilisateurs (UUID ou cookie)
    - Temps de traitement
    - Codes de réponse
    - Gestion sécurisée des cookies pour les utilisateurs anonymes
    """
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Initialise le middleware avec les loggers.
        
        Args:
            get_response: Fonction pour obtenir la réponse HTTP
        """
        self.get_response = get_response
        self.logger = LoggerFactory.get_default_logger('request')
        self.logger_home = LoggerFactory.get_default_logger()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Traite la requête et enregistre les informations de log.
        
        Args:
            request: Requête HTTP entrante
            
        Returns:
            HttpResponse: Réponse HTTP avec cookies de suivi si nécessaire
        """
        start_time = time.time()
        
        try:
            response = self.get_response(request)
            if request.user.is_authenticated:
                # Utiliser un hachage de l'UUID de l'utilisateur plutôt que l'UUID direct
                unique_id = str(request.user.uuid)
                log_id = f"USER_{unique_id}"
            else:
                # Récupérer ou générer un cookie sécurisé
                unique_id = request.COOKIES.get('unique_id')
                
                # Validation stricte du cookie
                try:
                    uuid.UUID(unique_id)
                except (ValueError, TypeError):
                    unique_id = None

                if not unique_id:
                    # Générer un UUID cryptographiquement sécurisé
                    unique_id = str(uuid.uuid4())
                    # Ajouter des drapeaux de sécurité au cookie
                    response.set_cookie(
                        'unique_id', 
                        unique_id, 
                        max_age=3600,
                        httponly=True,  # Empêche l'accès via JavaScript
                        secure=True,    # HTTPS uniquement
                        samesite='Strict'  # Protection contre les attaques CSRF
                    )
                log_id = f"COOKIE_{unique_id}"
   
            
            duration = round(time.time() - start_time, 6)

            # Filtrage des données sensibles
            filtered_post = {
                k: ("***" if any(sensitive in k.lower() for sensitive in ["password", "secret", "token"]) else v)
                for k, v in request.POST.items()
            }

            # Logging avec des informations minimales et sécurisées
            self.logger.info(
                '',
                extra={
                    'method': request.method,
                    'request': request.get_full_path(),
                    'post': filtered_post,
                    'status': response.status_code,
                    'duration': duration,
                    'unique_id': log_id
                }
            )
    
    
    
            self.logger_home.info(
                f"REQUEST : {request.method:<8} {request.get_full_path()} {filtered_post} {response.status_code} {duration}sec id:{log_id}"
            )

            return response

        except Exception as e:
            # Gestion des erreurs sans exposer de détails sensibles
            logging.error(f"Erreur dans le middleware de logging {e}")
            return self.get_response(request)