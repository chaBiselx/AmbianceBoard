import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from main.service.SoundBoardService import SoundBoardService
from main.interface.ui.forms.private.SoundBoardForm import SoundBoardForm
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum

from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum

from main.domain.common.utils.logger import logger


@login_required
@require_http_methods(['POST', 'GET'])
def soundboard_create(request):
    """Création d'un nouveau soundboard"""
    if request.method == 'POST':
        soundboard = (SoundBoardService(request)).save_form()
        ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.SOUNDBOARD_CREATE, user=request.user, content_object=soundboard)
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
            ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.SOUNDBOARD_DELETE, user=request.user, content_object=soundboard)
            soundboard.delete()
            return JsonResponse({'success': 'Suppression soundboard réussie'}, status=200)
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)


