from django import template

register = template.Library()

@register.inclusion_tag('partials/popupModerator.html')
def show_data_playlist(playlist):
    return  {'playlist': playlist, 'user' : playlist.user, 'soundboard' : None}
    
@register.inclusion_tag('partials/popupModerator.html')
def show_data_soundboard(soundboard):
    return  {'playlist': None, 'user' : soundboard.user, 'soundboard' : soundboard}

@register.inclusion_tag('partials/popupModerator.html')
def show_data_user(user):
    return  {'playlist': None, 'user' : user, 'soundboard' : None}