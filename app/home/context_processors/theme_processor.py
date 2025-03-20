from django.urls import reverse
from home.enum.ThemeEnum import ThemeEnum
from home.models.UserPreference import UserPreference

def theme_processor(request):
    # Liste des URLs où la sidebar doit apparaître
    
    if(request.user.is_authenticated):
        try:
            user_preference = UserPreference.objects.get(user=request.user)
            theme = user_preference.theme
            if theme != None:
                return {'theme': theme}
        except UserPreference.DoesNotExist:
            pass

    return {'theme': ThemeEnum.LIGHT.value}
    
    