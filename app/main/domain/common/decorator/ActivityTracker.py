"""
Décorateurs pour le traçage automatique des activités utilisateur.

Ces décorateurs permettent de tracer automatiquement les actions des utilisateurs
sans avoir à ajouter manuellement le code de traçage dans chaque vue.
"""

import functools
import uuid
from typing import Any, Callable, Optional, Dict
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from main.models.UserActivity import UserActivity
from main.enum.UserActivityTypeEnum import UserActivityTypeEnum


def track_user_activity(
    activity_type: UserActivityTypeEnum,
    get_content_object: Optional[Callable] = None
):
    """
    Décorateur pour tracer automatiquement l'activité utilisateur.
    
    Args:
        activity_type: Type d'activité à tracer
        get_content_object: Fonction pour récupérer l'objet associé (reçoit request, *args, **kwargs)
    
    Usage:
        @track_user_activity(UserActivityTypeEnum.PLAYLIST_VIEW)
        def playlist_detail(request, playlist_id):
            # Vue de détail de playlist
            pass
        
        @track_user_activity(
            UserActivityTypeEnum.SOUNDBOARD_PLAY,
            get_content_object=lambda req, *args, **kwargs: get_object_or_404(SoundBoard, pk=kwargs['pk'])
        )
        def play_soundboard(request, pk):
            # Vue de lecture de soundboard
            pass
    """
    def decorator(view_func: Callable) -> Callable:
        @functools.wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # Extraction des informations de la requête
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key
            user_agent = request.META.get('HTTP_USER_AGENT')
            referrer = request.META.get('HTTP_REFERER')
            
            # Récupération de l'objet associé si fonction fournie
            content_object = None
            if get_content_object:
                try:
                    content_object = get_content_object(request, *args, **kwargs)
                except Exception:
                    # Si erreur lors de la récupération de l'objet, on continue sans
                    content_object = None
            
            # Création de l'activité
            UserActivity.create_activity(
                activity_type=activity_type,
                user=user,
                content_object=content_object,
                session_key=session_key,
                user_agent=user_agent,
                referrer=referrer
            )
            
            # Exécution de la vue
            response = view_func(request, *args, **kwargs)
            
            return response
        
        return wrapper
    return decorator


def track_page_view(
    get_content_object: Optional[Callable] = None
):
    """
    Décorateur spécialisé pour tracer les vues de page.
    
    Ce décorateur est une version simplifiée de track_user_activity
    spécialement conçue pour tracer les vues de pages.
    
    Args:
        get_content_object: Fonction pour récupérer l'objet associé
    """
    return track_user_activity(
        activity_type=UserActivityTypeEnum.PAGE_VIEW,
        get_content_object=get_content_object
    )


def track_action(
    activity_type: UserActivityTypeEnum,
    get_content_object: Optional[Callable] = None
):
    """
    Décorateur spécialisé pour tracer les actions.
    
    Ce décorateur est une version simplifiée de track_user_activity
    spécialement conçue pour tracer les actions ponctuelles.
    
    Args:
        activity_type: Type d'activité à tracer
        get_content_object: Fonction pour récupérer l'objet associé
    """
    return track_user_activity(
        activity_type=activity_type,
        get_content_object=get_content_object
    )


class ActivityContextManager:
    """
    Gestionnaire de contexte pour tracer des activités avec durée.
    
    Permet de tracer des activités qui ne sont pas liées à des vues Django,
    comme des tâches en arrière-plan ou des opérations complexes.
    
    Usage:
        with ActivityContextManager(
            UserActivityTypeEnum.MUSIC_UPLOAD,
            user=request.user,
            content_object=playlist
        ) as activity:
            # Code d'upload de musique
            upload_music(file)
    """
    
    def __init__(
        self,
        activity_type: UserActivityTypeEnum,
        user: Optional[Any] = None,
    ):
        self.activity_type = activity_type
        self.user = user
    
    def action(self) -> 'ActivityContextManager':
        """Démarre le traçage de l'activité."""
        self.activity = UserActivity.create_activity(
            activity_type=self.activity_type,
            user=self.user,
        )
        return self
    



# Décorateurs pré-configurés pour les actions courantes
track_logout = track_action(UserActivityTypeEnum.LOGOUT)

# def track_playlist_view(view_func: Callable) -> Callable:
#     """Décorateur pour tracer les vues de playlist."""
#     def get_playlist(request, *args, **kwargs):
#         from main.models.Playlist import Playlist
#         from django.shortcuts import get_object_or_404
#         playlist_id = kwargs.get('pk') or kwargs.get('playlist_id') or args[0] if args else None
#         if playlist_id:
#             return get_object_or_404(Playlist, pk=playlist_id)
#         return None
    
#     return track_page_view(get_content_object=get_playlist)(view_func)

# def track_soundboard_view(view_func: Callable) -> Callable:
#     """Décorateur pour tracer les vues de soundboard."""
#     def get_soundboard(request, *args, **kwargs):
#         from main.models.SoundBoard import SoundBoard
#         from django.shortcuts import get_object_or_404
#         soundboard_id = kwargs.get('pk') or kwargs.get('soundboard_id') or args[0] if args else None
#         if soundboard_id:
#             return get_object_or_404(SoundBoard, pk=soundboard_id)
#         return None
    
#     return track_page_view(get_content_object=get_soundboard)(view_func)
