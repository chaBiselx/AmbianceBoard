from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape # counter XSS 
from main.domain.common.service.PlaylistDataService import PlaylistDataService

register = template.Library()

@register.filter
def applys_playlist_content(playlist):
    name = escape(playlist.name)
    content = f"{name}"
    if playlist.icon :
        content = f"<img class=\"playlist-img\" src=\"{playlist.icon.url }\" alt=\"{ name }\" draggable=\"false\" ></img>"
    
    return mark_safe(content)

@register.filter
def get_playlist_data(playlist):
    """
    Récupère les données de configuration de la playlist.
    
    Args:
        playlist: Instance du modèle Playlist
        
    Returns:
        Dict: Données de configuration de la playlist
    """
    service = PlaylistDataService()
    return service.get_playlist_data(playlist)
