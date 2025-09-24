from django import template
from main.architecture.ui.service.StaticFilesService import StaticFilesService

register = template.Library()

@register.simple_tag(takes_context=True)
def get_user_theme(context):
    request = context['request']
    user_preference = getattr(request.user, 'UserPreference', None)
    if user_preference and user_preference.theme:
        return user_preference.theme
    
    # Get theme from cookies
    cookie_theme = request.COOKIES.get('theme')
    if cookie_theme:
        return cookie_theme
    
    return 'light'

@register.simple_tag(takes_context=True)
def is_backend_saved(context):
    request = context['request']
    user_preference = getattr(request.user, 'UserPreference', None)
    if user_preference and user_preference.theme:
        return True
    return False
    
    