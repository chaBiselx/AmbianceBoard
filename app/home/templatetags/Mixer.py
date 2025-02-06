from django import template

register = template.Library()

@register.inclusion_tag('partials/mixer.html')
def add_mixer(playlist_list_enum):
    return  {'PlaylistTypeEnum': playlist_list_enum}
    
