from django.urls import reverse

def sidebar_processor(request):
    # Liste des URLs où la sidebar doit apparaître
    sidebar_urls_settings_account = ['/account/settings/']
    
    # Vérifiez si l'URL actuelle fait partie de celles qui nécessitent une sidebar
    if request.path in sidebar_urls_settings_account or any(request.path.startswith(url) for url in sidebar_urls_settings_account):
        return {
            'show_sidebar': True,
            'sidebar_items': [
                {'title': 'Index', 'url': reverse("settingsIndex"), 'classIcon':None},
                {'title': 'Playlist type', 'url': reverse("defaultPlaylistType"), 'classIcon':None},
                {'title': 'Dimensions boutons', 'url': reverse("updateDimensions"), 'classIcon':None},
            ]
        }
        
    sidebar_urls_settings_moderator = ['/moderator']
    
    if request.path in sidebar_urls_settings_moderator or any(request.path.startswith(url) for url in sidebar_urls_settings_moderator):
        return {
            'show_sidebar': True,
            'sidebar_items': [
                {'title': 'Dashboard', 'url': reverse("moderatorDashboard"), 'classIcon':"fa-solid fa-chart-line"},
                {'title': 'Soundboards', 'url': reverse("moderatorControleImagesSoundboard"), 'classIcon':"fa-solid fa-table-cells-large"},
                {'title': 'Playlists', 'url': reverse("moderatorControleImagesPlaylist"), 'classIcon':"fa-solid fa-music"},
                {'title': 'Report', 'url': reverse("moderatorControleReport"), 'classIcon':"fa-solid fa-helmet-safety"},
                {'title': 'Logs', 'url': reverse("moderatorControleLog"), 'classIcon':"fa-solid fa-helmet-safety"},
                {'title': 'Tags', 'url': reverse("moderatorListingTags"), 'classIcon':"fas fa-tags"},
            ]
        }
        
    sidebar_urls_settings_moderator = ['/manager']
    
    if request.path in sidebar_urls_settings_moderator or any(request.path.startswith(url) for url in sidebar_urls_settings_moderator):
        return {
            'show_sidebar': True,
            'sidebar_items': [
                {'title': 'User Tiers', 'url': reverse("adminUserTiersDashboard"), 'classIcon':"fa-solid fa-users-medical"},
     
            ]
        }
        
    if request.user.is_authenticated:
        sidebar_urls_settings_public = ['/public']
        
        
        if request.path in sidebar_urls_settings_public or any(request.path.startswith(url) for url in sidebar_urls_settings_public):
            return {
                'show_sidebar': True,
                'sidebar_items': [
                    {'title': 'Soundboard', 'url': reverse("publicListingSoundboard"), 'classIcon':"fa-solid fa-bars"},
                    {'title': 'Favoris', 'url': reverse("publicFavorite"), 'classIcon':"fa-regular fa-star"},
                ]
            }
    return {'show_sidebar': False}

