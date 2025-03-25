import uuid
import logging
import time
import secrets

class LogRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request')
        self.logger_home = logging.getLogger('home')

    def __call__(self, request):
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