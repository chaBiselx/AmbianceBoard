"""
Exemples d'utilisation du système de traçage d'activité utilisateur.

Ce fichier contient des exemples concrets d'utilisation des décorateurs
et services de traçage d'activité.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from django.contrib import messages

from main.decorator.ActivityTracker import (
    track_user_activity,
    track_page_view,
    track_action,
    track_playlist_view,
    track_soundboard_view,
    ActivityContextHelper
)
from main.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.service.UserActivityStatsService import UserActivityStatsService
from main.models.Playlist import Playlist
from main.models.SoundBoard import SoundBoard


# Exemple 1: Vue de liste de playlists avec traçage de page
@track_page_view()
def playlist_list(request):
    """
    Vue de liste des playlists avec traçage automatique de page.
    Le décorateur track_page_view trace automatiquement l'accès à la page
    et la durée de consultation.
    """
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'playlists/list.html', {'playlists': playlists})


# Exemple 2: Vue de détail de playlist avec objet associé
@track_playlist_view
def playlist_detail(request, pk):
    """
    Vue de détail d'une playlist avec traçage automatique.
    Le décorateur track_playlist_view récupère automatiquement
    l'objet Playlist et le trace.
    """
    playlist = get_object_or_404(Playlist, pk=pk)
    return render(request, 'playlists/detail.html', {'playlist': playlist})


# Exemple 3: Action de lecture simplifiée
@track_user_activity(
    UserActivityTypeEnum.PLAYLIST_PLAY,
    get_content_object=lambda req, *args, **kwargs: get_object_or_404(Playlist, pk=kwargs['pk'])
)
@require_http_methods(["POST"])
def play_playlist(request, pk):
    """
    Action de lecture d'une playlist avec traçage de l'objet.
    Trace l'action avec l'objet playlist associé.
    """
    playlist = get_object_or_404(Playlist, pk=pk)
    # Logique de lecture de la playlist
    return JsonResponse({'status': 'playing', 'playlist_id': playlist.id})


# Exemple 4: Création avec gestionnaire de contexte
@login_required
def create_playlist(request):
    """
    Création d'une playlist avec traçage via gestionnaire de contexte.
    Permet de tracer la durée de création.
    """
    if request.method == 'POST':
        with ActivityContextHelper(
            request, 
            UserActivityTypeEnum.PLAYLIST_CREATE,
            user=request.user,
            session_key=request.session.session_key
        ) as activity:
            
            # Processus de création
            playlist = Playlist.objects.create(
                user=request.user,
                name=request.POST.get('name'),
                typePlaylist=request.POST.get('type')
            )
            
            # Association de l'objet créé à l'activité
            if activity.activity:
                activity.activity.content_object = playlist
                activity.activity.save()
        
        messages.success(request, 'Playlist créée avec succès!')
        return redirect('playlist_detail', pk=playlist.pk)
    
    return render(request, 'playlists/create.html')


# Exemple 5: Authentification avec traçage
@track_action(UserActivityTypeEnum.LOGIN)
def user_login(request):
    """
    Vue de connexion avec traçage automatique.
    """
    if request.method == 'POST':
        # Logique d'authentification
        # login(request, user)
        pass
    
    return render(request, 'auth/login.html')


@track_action(UserActivityTypeEnum.LOGOUT)
def user_logout(request):
    """
    Vue de déconnexion avec traçage automatique.
    """
    logout(request)
    return redirect('home')


# Exemple 6: Vue d'administration avec statistiques
@login_required
def admin_stats(request):
    """
    Vue d'administration affichant les statistiques d'activité.
    """
    # Statistiques générales
    activity_counts = UserActivityStatsService.get_activity_counts_by_type(days=30)
    
    # Utilisateurs les plus actifs
    most_active = UserActivityStatsService.get_most_active_users(limit=10)
    
    # Analyses de session
    session_analytics = UserActivityStatsService.get_session_analytics()
    
    # Engagement des playlists
    playlist_engagement = UserActivityStatsService.get_content_engagement_stats('playlist')
    
    # Pattern d'activité par heure
    hourly_pattern = UserActivityStatsService.get_hourly_activity_pattern()
    
    context = {
        'activity_counts': activity_counts,
        'most_active_users': most_active,
        'session_analytics': session_analytics,
        'playlist_engagement': playlist_engagement,
        'hourly_pattern': hourly_pattern,
    }
    
    return render(request, 'admin/stats.html', context)


# Exemple 7: API avec traçage de recherche
@track_user_activity(UserActivityTypeEnum.SEARCH)
def search_api(request):
    """
    API de recherche avec traçage des requêtes.
    """
    query = request.GET.get('q', '')
    
    # Recherche dans les playlists et soundboards
    playlists = Playlist.objects.filter(name__icontains=query)[:10]
    soundboards = SoundBoard.objects.filter(name__icontains=query)[:10]
    
    results = {
        'playlists': [{'id': p.id, 'name': p.name} for p in playlists],
        'soundboards': [{'id': s.id, 'name': s.name} for s in soundboards],
        'total': playlists.count() + soundboards.count()
    }
    
    return JsonResponse(results)


# Exemple 8: Traçage d'erreurs personnalisé
def custom_404_view(request):
    """
    Vue d'erreur 404 personnalisée avec traçage.
    """
    # Traçage manuel de l'erreur 404
    from main.models.UserActivity import UserActivity
    
    UserActivity.create_activity(
        activity_type=UserActivityTypeEnum.ERROR_404,
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key,
    )
    
    return render(request, '404.html', status=404)


# Exemple 9: Middleware pour traçage automatique des pages
class ActivityTrackingMiddleware:
    """
    Middleware pour tracer automatiquement toutes les vues de page.
    
    À ajouter dans settings.py dans MIDDLEWARE:
    'main.middleware.ActivityTrackingMiddleware',
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Traçage automatique de la vue de page
        if request.method == 'GET' and not request.path.startswith('/api/'):
            from main.models.UserActivity import UserActivity
            
            UserActivity.create_activity(
                activity_type=UserActivityTypeEnum.PAGE_VIEW,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
            )
        
        response = self.get_response(request)
        
        return response


# Exemple 10: Tâche Celery avec traçage
from celery import shared_task

@shared_task
def process_music_upload(user_id, music_file_path, playlist_id):
    """
    Tâche Celery pour traiter l'upload de musique avec traçage.
    """
    from django.contrib.auth import get_user_model
    from main.models.UserActivity import UserActivity
    
    user_model = get_user_model()
    user = user_model.objects.get(id=user_id)
    playlist = Playlist.objects.get(id=playlist_id)
    
    with ActivityContextHelper(
        request, 
        UserActivityTypeEnum.MUSIC_UPLOAD,
        user=user,
        content_object=playlist
    ):
        
        # Simulation du traitement
        import time
        time.sleep(5)  # Simulation du traitement
    
    return {'status': 'success', 'playlist_id': playlist_id}
