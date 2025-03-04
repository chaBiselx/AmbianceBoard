import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from home.service.PlaylistService import PlaylistService
from home.forms.PlaylistColorUserForm import PlaylistColorUserForm
from home.models.PlaylistColorUser import PlaylistColorUser
from django.forms import formset_factory
from home.service.DefaultColorPlaylistService import DefaultColorPlaylistService

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

