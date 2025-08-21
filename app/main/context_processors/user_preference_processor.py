from django.urls import reverse
from main.domain.common.enum.ThemeEnum import ThemeEnum
from main.models.UserPreference import UserPreference
from main.utils.UserTierManager import UserTierManager

def user_preference_processor(request):
    # Liste des URLs où la sidebar doit apparaître
    theme = None
    soundboard_dim = None
    playlist_dim = None
    can_share_soundboard = False
    
    if(request.user.is_authenticated):
        try:
            user_preference = UserPreference.objects.get(user=request.user)
            theme_temp = user_preference.theme
            if theme_temp != None:
                theme = theme_temp
            soundboard_dim_temp = user_preference.soundboardDim
            if soundboard_dim_temp != None:
                soundboard_dim = soundboard_dim_temp
            playlist_dim_temp = user_preference.playlistDim
            if playlist_dim_temp != None:
                playlist_dim = playlist_dim_temp

        except UserPreference.DoesNotExist:
            pass
        
        # Vérifier si l'utilisateur peut partager des soundboards
        can_share_soundboard = UserTierManager.can_user_share_soundboard(request.user)
        
    if theme == None:
        theme = ThemeEnum.LIGHT.value
    if soundboard_dim == None:
        soundboard_dim = 100
    if playlist_dim == None:
        playlist_dim = 100
    return {
        'theme': theme, 
        'soundboard_dim': soundboard_dim, 
        'playlist_dim': playlist_dim,
        'can_share_soundboard': can_share_soundboard
    }
    
    