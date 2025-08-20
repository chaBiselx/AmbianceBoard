"""
Middleware pour la gestion et le traçage des erreurs HTTP.

Middleware responsable du traçage des erreurs 4XX et 5XX dans l'application,
permettant de collecter des statistiques sur les erreurs rencontrées par les utilisateurs.
"""

from typing import Callable
from django.http import HttpRequest, HttpResponse
from main.models.UserActivity import UserActivity
from main.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.utils.logger import LoggerFactory


class ErrorTrackingMiddleware:
    """
    Middleware pour le traçage des erreurs HTTP.
    
    Ce middleware intercepte les réponses HTTP avec des codes d'erreur
    (4XX et 5XX) et enregistre ces erreurs comme des activités utilisateur
    pour permettre leur analyse statistique.
    """
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Initialise le middleware avec les loggers.
        
        Args:
            get_response: Fonction pour obtenir la réponse HTTP
        """
        self.get_response = get_response
        self.logger = LoggerFactory.get_default_logger()
        
        # Mapping des codes d'erreur vers les types d'activité
        self.error_mapping = {
            404: UserActivityTypeEnum.ERROR_404,
            405: UserActivityTypeEnum.ERROR_405,
            406: UserActivityTypeEnum.ERROR_406,
            429: UserActivityTypeEnum.ERROR_429,
            500: UserActivityTypeEnum.ERROR_500,
        }
        
        # URLs à exclure du traçage d'erreurs (patterns)
        self.excluded_url_patterns = [
            # Chrome DevTools et outils de développement
            "/.well-known/appspecific/com.chrome.devtools.json",
            "/.well-known/",
            "/favicon.ico",
            "/robots.txt",
            "/sitemap.xml",
            "/apple-touch-icon",
            "/browserconfig.xml",
            "/manifest.json",
            
            # Fichiers système et sécurité
            "/.env",
            "/.git/",
            "/wp-admin/",
            "/wp-content/",
            "/wp-includes/",
            "/phpmyadmin/",
            "/admin.php",
            "/xmlrpc.php",
            
            # Scans de sécurité communs
            "/config.php",
            "/setup.php",
            "/install.php",
            "/.htaccess",
            "/web.config",
            
            # Bots et crawlers
            "/ads.txt",
            "/security.txt",
            "/.DS_Store",
            "/thumbs.db",
        ]

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Traite la requête et enregistre les erreurs si nécessaire.
        
        Args:
            request: Requête HTTP entrante
            
        Returns:
            HttpResponse: Réponse HTTP
        """
        try:
            response = self.get_response(request)
            
            # Vérifier si la réponse contient une erreur
            if response.status_code >= 400:
                self._track_error(request, response.status_code)
            
            return response
            
        except Exception as e:
            # Gestion des erreurs 5XX non prévues
            self.logger.error(f"Erreur inattendue dans ErrorTrackingMiddleware: {e}")
            response = self.get_response(request)
            
            # Tracer l'erreur 500 générique
            self._track_error(request, 500)
            
            return response

    def _should_exclude_url(self, request: HttpRequest) -> bool:
        """
        Vérifie si l'URL de la requête doit être exclue du traçage.
        
        Args:
            request: Requête HTTP
            
        Returns:
            bool: True si l'URL doit être exclue, False sinon
        """
        path = request.get_full_path()
        
        # Vérifier chaque pattern d'exclusion
        for pattern in self.excluded_url_patterns:
            if pattern.endswith('/'):
                # Pattern de dossier - vérifier si le chemin commence par ce pattern
                if path.startswith(pattern):
                    return True
            else:
                # Pattern de fichier - vérifier correspondance exacte ou si le chemin se termine par ce pattern
                if path == pattern or path.endswith(pattern):
                    return True
        
        return False

    def _track_error(self, request: HttpRequest, status_code: int) -> None:
        """
        Enregistre l'erreur comme une activité utilisateur.
        
        Args:
            request: Requête HTTP
            status_code: Code de statut HTTP de l'erreur
        """
        try:
            # Vérifier si cette URL doit être exclue du traçage
            if self._should_exclude_url(request):
                self.logger.debug(
                    f"URL exclue du traçage d'erreur: {request.get_full_path()} (status: {status_code})"
                )
                return
            
            # Déterminer le type d'activité basé sur le code d'erreur
            activity_type = self._get_activity_type_for_status(status_code)
            
            if activity_type:
                # Récupérer l'utilisateur s'il est connecté
                user = request.user if request.user.is_authenticated else None
                
                # Récupérer la clé de session pour les utilisateurs anonymes
                session_key = request.session.session_key if hasattr(request, 'session') else None
                
                # Créer l'activité d'erreur
                UserActivity.create_activity(
                    activity_type=activity_type,
                    user=user,
                    session_key=session_key,
                )
                
                # Logger l'erreur pour debug
                user_info = f"User {user.username}" if user else f"Anonymous (session: {session_key})"
                self.logger.warning(
                    f"Erreur {status_code} tracée pour {user_info} sur {request.get_full_path()}"
                )
                
        except Exception as e:
            # En cas d'erreur lors du traçage, ne pas faire échouer la requête
            self.logger.error(f"Erreur lors du traçage de l'erreur {status_code}: {e}")

    def _get_activity_type_for_status(self, status_code: int) -> UserActivityTypeEnum:
        """
        Détermine le type d'activité basé sur le code de statut.
        
        Args:
            status_code: Code de statut HTTP
            
        Returns:
            UserActivityTypeEnum: Type d'activité correspondant ou None
        """
        # Codes d'erreur spécifiques
        if status_code in self.error_mapping:
            return self.error_mapping[status_code]
        
        # Erreurs 4XX génériques
        elif 400 <= status_code < 500:
            return UserActivityTypeEnum.ERROR_4XX
        
        # Erreurs 5XX génériques
        elif 500 <= status_code < 600:
            return UserActivityTypeEnum.ERROR_5XX
        
        # Pas une erreur à tracer
        return None

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """
        Traite les exceptions non gérées.
        
        Args:
            request: Requête HTTP
            exception: Exception levée
        """
        try:
            # Vérifier si cette URL doit être exclue du traçage
            if not self._should_exclude_url(request):
                # Tracer l'erreur 500 pour les exceptions non gérées
                self._track_error(request, 500)
            
            # Logger l'exception
            self.logger.error(
                f"Exception non gérée: {type(exception).__name__}: {str(exception)}",
                extra={
                    'request_path': request.get_full_path(),
                    'request_method': request.method,
                    'user': str(request.user) if request.user.is_authenticated else 'Anonymous'
                }
            )
            
        except Exception as e:
            # En cas d'erreur lors du traçage, ne pas faire échouer la requête
            self.logger.error(f"Erreur lors du traçage de l'exception: {e}")
