from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape # counter XSS 

register = template.Library()

@register.filter
def applys_soundboard_content(playlist):
    name = escape(playlist.name)
    content = f"{name}"
    if playlist.icon :
        content = f"<img class=\"playlist-img\" src=\"{playlist.icon.url }\" alt=\"{ name }\" draggable=\"false\" ></img>"
    
    return mark_safe(content)    

@register.filter
def get_name(soundboard):
    return f"{escape(soundboard.name)}"


@register.filter
def get_ordered_playlists(soundboard, owner):
    """Return ordered playlists with public mode enabled for non-owners."""
    from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository

    return SoundboardPlaylistRepository().get_sectioned_playlists(soundboard, public=(not bool(owner)))