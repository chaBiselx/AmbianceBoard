from django import template
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.service.DefaultColorPlaylistService import DefaultColorPlaylistService

register = template.Library()

@register.filter
def to_value(name):
    return PlaylistTypeEnum[name].value

@register.simple_tag(takes_context=True)
def get_playlist_type_style(context, playlist_type_name):
    user = context.get('request').user if context.get('request') else None
    if not user or not user.is_authenticated:
        default_colors = PlaylistTypeEnum[playlist_type_name].get_default_color()
        return f"background-color: {default_colors['color']}; color: {default_colors['colorText']};"

    service = DefaultColorPlaylistService(user)
    return f"background-color: {service.get_default_color(playlist_type_name)}; color: {service.get_default_color_text(playlist_type_name)};"

@register.simple_tag
def get_playlist_type_short_description(playlist_type_name):
    return PlaylistTypeEnum[playlist_type_name].get_short_description()

