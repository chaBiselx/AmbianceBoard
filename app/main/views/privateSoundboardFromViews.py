import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from main.models.SoundBoard import SoundBoard
from main.manager.SoundBoardPlaylistManager import SoundBoardPlaylistManager
from main.service.SoundBoardService import SoundBoardService
from main.service.PlaylistService import PlaylistService
from main.service.SoundboardPlaylistService import SoundboardPlaylistService
from main.service.SharedSoundboardService import SharedSoundboardService
from main.forms.SoundBoardForm import SoundBoardForm
from main.filters.SoundBoardFilter import SoundBoardFilter
from main.enum.PermissionEnum import PermissionEnum
from main.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.enum.ConfigTypeDataEnum import ConfigTypeDataEnum
from main.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.enum.ErrorMessageEnum import ErrorMessageEnum
from django.core import exceptions

from main.utils.logger import logger


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


