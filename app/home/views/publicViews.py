import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from home.utils.ExtractPaginator import extract_context_to_paginator
from home.models.SoundBoard import SoundBoard
from home.service.SoundBoardService import SoundBoardService
from home.service.MusicService import MusicService
from home.decorator.detectBan import detect_ban
from home.decorator.reportingContent import add_reporting_btn
from django.template.response import TemplateResponse
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from django.views.decorators.http import require_http_methods
from home.models.UserFavoritePublicSoundboard import UserFavoritePublicSoundboard
from home.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from home.enum.ErrorMessageEnum import ErrorMessageEnum
from django.contrib import messages
from home.service.ReportContentService import ReportContentService
from home.service.SharedSoundboardService import SharedSoundboardService



@require_http_methods(['GET'])
def public_index(request):
    return redirect('publicListingSoundboard')

@require_http_methods(['GET'])
@add_reporting_btn()
def public_listing_soundboard(request):
    page_number = int(request.GET.get('page', 1))
    
    list_favorite = []
    if request.user.is_authenticated:
        list_favorite_obj = request.user.favorite.all()
        for favorite in list_favorite_obj:
            list_favorite.append(favorite.get_soundboard().uuid)
    
    
    queryset = SoundBoard.objects.filter(is_public=True, user__isBan = False).order_by('uuid')
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['listFavorite'] = list_favorite
    return TemplateResponse(request, 'Html/Public/listing_soundboard.html', context)

@require_http_methods(['GET'])
@detect_ban
@add_reporting_btn()
def public_soundboard_read_playlist(request, soundboard_uuid):
    soundboard = (SoundBoardService(request)).get_public_soundboard(soundboard_uuid)
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    else:   
        return TemplateResponse(request, 'Html/Public/soundboard_read.html', {'soundboard': soundboard, 'PlaylistTypeEnum' : list(PlaylistTypeEnum) })
    
@require_http_methods(['GET'])
@detect_ban
def public_music_stream(request, soundboard_uuid, playlist_uuid) -> HttpResponse:
 
    music = (MusicService(request)).get_public_random_music(soundboard_uuid, playlist_uuid)
    if not music :
        return HttpResponse("Musique introuvable.", status=404)
    
    SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, music)
    
    response = HttpResponse(music.file, content_type='audio/*')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(music.fileName)
    return response

@login_required
@require_http_methods(['UPDATE'])
def public_stop_stream(request, soundboard_uuid, playlist_uuid) -> JsonResponse:
    
    SharedSoundboardService(request, soundboard_uuid).music_stop(playlist_uuid)
    
    return JsonResponse({"message": "stream stop"}, status=200)
@login_required
@require_http_methods(['POST', 'DELETE'])
def favorite_update(request, soundboard_uuid) -> JsonResponse:
    logger = logging.getLogger('home')
    try:
        soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
    except SoundBoard.DoesNotExist:
        return JsonResponse({"error": "SoundBoard introuvable."}, status=404)
    
    if request.method == 'POST':
        try:
            _, _ = UserFavoritePublicSoundboard.objects.get_or_create(user=request.user, uuidSoundboard=soundboard)
            return JsonResponse({"message": "success"}, status=200)

        except Exception as e:
            logger.error(f"favorite_update : {e}")
            return JsonResponse({"error": ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)
            
    if request.method == 'DELETE':
        try:
            favorite = request.user.favorite.get(uuidSoundboard=soundboard)
            favorite.delete()
            return JsonResponse({"message": "success"}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Favorite not found."}, status=404)
        except Exception as e:
            logger.error(f"favorite_update : {e}")
            return JsonResponse({"error": ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)
        
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)
   
@require_http_methods(['POST'])
def reporting_content(request):
    if request.method == 'POST':
        
        if(ReportContentService(request).save_report()):
            messages.info(request, 'Votre signalement a bien été pris en compte, merci de votre contribution')
        else : 
            messages.error(request, 'Une erreur est survenue, merci de re-essayer plus tard')
        
        
        if(request.POST.get('redirect')):
            return redirect(request.POST.get('redirect'))
        else:
            return redirect('publicListingSoundboard')
    return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)


    