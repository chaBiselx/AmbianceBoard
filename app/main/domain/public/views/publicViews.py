from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from main.utils.ExtractPaginator import extract_context_to_paginator
from main.models.SoundBoard import SoundBoard
from main.service.SoundBoardService import SoundBoardService
from main.service.MusicService import MusicService
from main.service.RandomizeTrackService import RandomizeTrackService
from main.domain.public.decorator.detectBan import detect_ban
from main.domain.public.decorator.reportingContent import add_reporting_btn
from django.template.response import TemplateResponse
from main.enum.PlaylistTypeEnum import PlaylistTypeEnum
from django.views.decorators.http import require_http_methods
from main.models.Tag import Tag
from django.db.models import Count
from main.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.enum.ErrorMessageEnum import ErrorMessageEnum
from main.service.ReportContentService import ReportContentService
from main.service.SharedSoundboardService import SharedSoundboardService
from main.service.TagService import TagService
from main.utils.url import redirection_url
from main.models.UserFavoritePublicSoundboard import UserFavoritePublicSoundboard
from main.utils.logger import logger
from main.utils.ServerNotificationBuilder import ServerNotificationBuilder

from main.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper

@require_http_methods(['GET'])
def public_index(request):
    return redirect('publicListingSoundboard')

@require_http_methods(['GET'])
@add_reporting_btn()
def public_listing_soundboard(request):
    page_number = int(request.GET.get('page', 1))
    selected_tag = request.GET.get('tag', None)
    
    list_favorite = []
    if request.user.is_authenticated:
        list_favorite_obj = request.user.favorite.all()
        for favorite in list_favorite_obj:
            list_favorite.append(favorite.get_soundboard().uuid)
    
    # Filtrage par tag si spécifié
    queryset = SoundBoard.objects.filter(is_public=True, user__isBan=False)
    if selected_tag:
        queryset = queryset.filter(tags__name=selected_tag)
    
    queryset = queryset.order_by('uuid')
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    
    
    context['listTags'] = TagService(request).get_tag_with_count()
    context['listFavorite'] = list_favorite
    context['selected_tag'] = selected_tag
    return TemplateResponse(request, 'Html/Public/listing_soundboard.html', context)

@require_http_methods(['GET'])
@login_required
def public_favorite(request):
    page_number = int(request.GET.get('page', 1))
    
    list_favorite = []
    if request.user.is_authenticated:
        list_favorite_obj = request.user.favorite.all()
        for favorite in list_favorite_obj:
            list_favorite.append(favorite.get_soundboard().uuid)
            
    
    queryset = SoundBoard.objects.filter(
        favorite__user=request.user,
        is_public=True, 
        user__isBan=False
    ).order_by('uuid')
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['listFavorite'] = list_favorite
    return TemplateResponse(request, 'Html/Public/listing_soundboard.html', context)


@require_http_methods(['GET'])
@detect_ban
@add_reporting_btn()
def public_soundboard_read_playlist(request, soundboard_uuid):
    SharedSoundboardService(request, soundboard_uuid).music_stop_all()
    soundboard = (SoundBoardService(request)).get_public_soundboard(soundboard_uuid)
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    else:   
        activity = ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.SOUNDBOARD_VIEW, user=request.user, content_object=soundboard)
        return TemplateResponse(request, 'Html/Public/soundboard_read.html', {
            'soundboard': soundboard, 
            'PlaylistTypeEnum' : list(PlaylistTypeEnum),
            'trace_user_activity': activity 
        })
    
@require_http_methods(['GET'])
@detect_ban
def public_music_stream(request, soundboard_uuid, playlist_uuid) -> HttpResponse:
 
    track = (RandomizeTrackService(request)).generate_public(soundboard_uuid, playlist_uuid)
    if not track :
        return HttpResponse("Musique introuvable.", status=404)
    
    SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, track)
    
    response = track.get_reponse_content()
    if(not response):
        return HttpResponse(ErrorMessageEnum.INTERNAL_SERVER_ERROR.value, status=500)
    return response

@login_required
@require_http_methods(['UPDATE'])
def public_stop_stream(request, soundboard_uuid, playlist_uuid) -> JsonResponse:
    
    SharedSoundboardService(request, soundboard_uuid).music_stop(playlist_uuid)
    
    return JsonResponse({"message": "stream stop"}, status=200)
@login_required
@require_http_methods(['POST', 'DELETE'])
def favorite_update(request, soundboard_uuid) -> JsonResponse:
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
        report = ReportContentService(request).save_report()
        if report:
            ServerNotificationBuilder(request).set_message("Votre signalement a bien été pris en compte, merci de votre contribution").set_statut("info").send()
            ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.REPORT_CONTENT, user=request.user, content_object=report)
        else : 
            ServerNotificationBuilder(request).set_message("Une erreur est survenue, merci de re-essayer plus tard").set_statut("error").send()

        
        if(request.POST.get('redirect')):
            return redirect(redirection_url(request.POST.get('redirect')))
        else:
            return redirect('publicListingSoundboard')
    return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)



    