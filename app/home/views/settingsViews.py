import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from home.service.PlaylistService import PlaylistService
from home.forms.PlaylistColorUserForm import PlaylistColorUserForm
from home.models.PlaylistColorUser import PlaylistColorUser
from home.models.UserPreference import UserPreference
from django.forms import formset_factory
from home.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from home.enum.ThemeEnum import ThemeEnum

PlaylistColorUserFormSet = formset_factory(PlaylistColorUserForm, extra=0)
logger = logging.getLogger('home')

@login_required
@require_http_methods(['GET'])
def settings_index(request):
    return render(request, 'Html/Account/Settings/index.html')

@login_required
@require_http_methods(['POST', 'GET'])
def settings_update_default_style(request):
    
    default_color_playlist = DefaultColorPlaylistService(request.user)
    initial_data = default_color_playlist.get_list_default_color()

    if request.method == "POST":
        formset = PlaylistColorUserFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    type_playlist = form.cleaned_data["typePlaylist"]
                    color = form.cleaned_data["color"]
                    color_text = form.cleaned_data["colorText"]
                    
                    # Mise à jour ou création de l'entrée
                    pcu, created = PlaylistColorUser.objects.get_or_create(user=request.user, typePlaylist=type_playlist)
                    pcu.color = color
                    pcu.colorText = color_text
                    if(created):
                        pcu.user = request.user
                        logger.debug(f"pcu.user: {pcu}")
                    pcu.save()
            
            return redirect('defaultPlaylistType')
    else:
        formset = PlaylistColorUserFormSet(initial=initial_data)
    
    return render(request, 'Html/Account/Settings/update_default_style_playlist.html', {'formset': formset})

@login_required
@require_http_methods(['UPDATE'])
def update_theme(request):
    if request.method == 'UPDATE':
        try:
            data = json.loads(request.body)  # Décode le JSON
            if 'theme' not in data:
                raise Exception('Theme not found in request data.')
            
            new_theme = data['theme']
            enum_theme = ThemeEnum(new_theme)
            user_preference, _ = UserPreference.objects.get_or_create(user=request.user)
            user_preference.theme = enum_theme.value
            user_preference.save()
            return JsonResponse({'message': 'Theme updated successfully.'}, status=200)
        except Exception as e:
            logger.error(f"update theme error : {e}")
            return JsonResponse({'error': 'Failed to update theme.'}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)