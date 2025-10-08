"""
Middleware pour la gestion des sessions quotidiennes et mise à jour du last_login.

Ce middleware vérifie si l'utilisateur connecté a une session active pour le jour actuel.
Si la session date d'un jour différent, il met à jour le champ last_login de l'utilisateur
et enregistre la nouvelle date de session.
"""

from typing import Callable
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from main.domain.common.utils.logger import LoggerFactory
import datetime

User = get_user_model()


class DailySessionMiddleware:
    """
    Middleware pour la gestion des sessions quotidiennes.
    
    Fonctionnalités :
    - Sauvegarde la date du jour dans la session
    - Met à jour le champ last_login si la session est d'un jour différent
    - Optimise les requêtes en évitant les mises à jour inutiles
    """
    
    SESSION_DATE_KEY = 'daily_session_date'
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Initialise le middleware.
        
        Args:
            get_response: Fonction pour obtenir la réponse HTTP
        """
        self.get_response = get_response
        self.logger = LoggerFactory.get_default_logger()
        self.now = timezone.now()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Traite la requête et gère la session quotidienne.
        
        Args:
            request: Requête HTTP entrante
            
        Returns:
            HttpResponse: Réponse HTTP
        """
        try:
            # Vérifier si l'utilisateur est connecté
            if request.user.is_authenticated and not request.user.is_anonymous:
                self._process_daily_session(request)
                
        except Exception as e:
            # Ne pas interrompre le flux de l'application en cas d'erreur
            self.logger.error(f"Erreur dans DailySessionMiddleware: {e}")
        
        response = self.get_response(request)
        return response
    
    def _process_daily_session(self, request: HttpRequest) -> None:
        """
        Traite la session quotidienne pour un utilisateur authentifié.
        
        Args:
            request: Requête HTTP avec utilisateur authentifié
        """
        current_date = self.now.date()
        session_date_str = request.session.get(self.SESSION_DATE_KEY)
        
        # Convertir la date de session si elle existe
        session_date = None
        if session_date_str:
            try:
                session_date = datetime.datetime.strptime(session_date_str, '%Y-%m-%d').date()
            except ValueError:
                # Format de date invalide, traiter comme une nouvelle session
                session_date = None
        
        # Si c'est une nouvelle session ou une session d'un jour différent
        if session_date != current_date:
            self._update_user_last_login(request.user, session_date)
            
            # Mettre à jour la session avec la nouvelle date
            request.session[self.SESSION_DATE_KEY] = current_date.strftime('%Y-%m-%d')

    
    def _update_user_last_login(self, user: User, previous_session_date: datetime.date = None) -> None:
        """
        Met à jour le champ last_login de l'utilisateur.
        
        Args:
            user: Instance de l'utilisateur
            current_date: Date actuelle
            previous_session_date: Date de la session précédente (peut être None)
        """
        try:
            # Utiliser update() pour éviter les conflits de concurrence
            User.objects.filter(pk=user.pk).update(last_login=self.now )
            
            # Mettre à jour l'instance en mémoire pour cohérence
            user.last_login = self.now 
            
            self.logger.info(
                f"last_login mis à jour pour {user.username}: {self.now}"
                + (f" (session précédente: {previous_session_date})" if previous_session_date else " (première session)")
            )
            
        except Exception as e:
            self.logger.error(
                f"Erreur lors de la mise à jour du last_login pour {user.username}: {e}"
            )