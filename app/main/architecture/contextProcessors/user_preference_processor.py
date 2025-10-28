from django.urls import reverse
from main.domain.common.enum.ThemeEnum import ThemeEnum
from main.architecture.persistence.repository.UserPreferenceRepository import UserPreferenceRepository
from main.architecture.persistence.repository.UserDevicePreferenceRepository import UserDevicePreferenceRepository
from main.domain.common.utils.UserTierManager import UserTierManager
from main.domain.common.utils.DeviceDetector import detect_device_type

def user_preference_processor(request):
    """
    Processeur de contexte pour les préférences utilisateur avec support des appareils.
    """
    theme = None
    soundboard_dim = None
    playlist_dim = None
    can_share_soundboard = False
    device_type = detect_device_type(request)
    can_shared_playlist_playable_by_shared_user = False
    
    if request.user.is_authenticated:
        # Récupérer les préférences générales
        user_preference = UserPreferenceRepository().get_user_preferences(request.user)
        
        if user_preference:
            # Utiliser le thème général par défaut
            theme = user_preference.theme
            
            # Chercher les préférences spécifiques à l'appareil
            device_preference = UserDevicePreferenceRepository().get_user_preferences(user_preference, device_type)
            if device_preference:
                # Utiliser les valeurs spécifiques à l'appareil si disponibles
                soundboard_dim = device_preference.get_effective_soundboard_dim()
                playlist_dim = device_preference.get_effective_playlist_dim()
                
        
        # Vérifier si l'utilisateur peut partager des soundboards
        can_share_soundboard = UserTierManager.can_boolean(request.user, 'share_soundboard')
        can_shared_playlist_playable_by_shared_user = UserTierManager.can_boolean(request.user, 'shared_playlist_playable_by_shared_user')

    if theme is None:
        theme = ThemeEnum.LIGHT.value
    if soundboard_dim is None:
        soundboard_dim = 100
    if playlist_dim is None:
        playlist_dim = 100
    
    return {
        'theme': theme,
        'soundboard_dim': soundboard_dim,
        'playlist_dim': playlist_dim,
        'can_share_soundboard': can_share_soundboard,
        'can_shared_playlist_playable_by_shared_user': can_shared_playlist_playable_by_shared_user,
        'device_type': device_type
    }
    
    