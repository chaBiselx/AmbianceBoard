from django.urls import reverse

def sidebar_processor(request):
    # Liste des URLs où la sidebar doit apparaître
    sidebar_urls = ['/account/settings/']
    
    print(request.path)
    
    # Vérifiez si l'URL actuelle fait partie de celles qui nécessitent une sidebar
    if request.path in sidebar_urls or any(request.path.startswith(url) for url in sidebar_urls):
        return {
            'show_sidebar': True,
            'sidebar_items': [
                {'title': 'Index', 'url': reverse("settingsIndex")},
                {'title': 'Playlist type', 'url': reverse("defaultPlaylistType")},
                {'title': 'Dimensions boutons', 'url': reverse("updateDimensions")},
            ]
        }
    return {'show_sidebar': False}

