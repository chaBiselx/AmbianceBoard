import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from home.models.SoundBoard import SoundBoard
from home.manager.SoundBoardPlaylistManager import SoundBoardPlaylistManager
from home.service.SoundBoardService import SoundBoardService
from home.service.PlaylistService import PlaylistService
from home.service.SoundboardPlaylistService import SoundboardPlaylistService
from home.service.SharedSoundboardService import SharedSoundboardService
from home.forms.SoundBoardForm import SoundBoardForm
from home.filters.SoundBoardFilter import SoundBoardFilter
from home.enum.PermissionEnum import PermissionEnum
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.enum.ConfigTypeDataEnum import ConfigTypeDataEnum
from home.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from home.enum.ErrorMessageEnum import ErrorMessageEnum
from django.core import exceptions

logger = logging.getLogger('home')


@login_required
@require_http_methods(['POST', 'GET'])
def soundboard_create(request):
    """Création d'un nouveau soundboard"""
    if request.method == 'POST':
        (SoundBoardService(request)).save_form()
        return redirect('soundboardsList')
    else:
        form = SoundBoardForm()
    return render(request, 'Html/Soundboard/soundboard_form.html', {'form': form, 'method': 'create'})



@login_required
@require_http_methods(['POST', 'GET'])
def soundboard_update(request, soundboard_uuid):
    """Mise à jour d'un soundboard"""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if request.method == 'POST':
        if not soundboard:
            return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
        else:
            form = SoundBoardForm(request.POST, request.FILES, instance=soundboard)
            if form.is_valid():
                form.save()
                return redirect('soundboardsList')
    else:
        if not soundboard:
            return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
        else:
            form = SoundBoardForm(instance=soundboard)
    return render(request, 'Html/Soundboard/soundboard_form.html', {'form': form, 'method': 'update'})


@login_required
@require_http_methods(['DELETE'])
def soundboard_delete(request, soundboard_uuid) -> JsonResponse:
    """Suppression d'un soundboard"""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if request.method == 'DELETE':
        if not soundboard:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        else:
            soundboard.delete()
            return JsonResponse({'success': 'Suppression soundboard réussie'}, status=200)
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)


