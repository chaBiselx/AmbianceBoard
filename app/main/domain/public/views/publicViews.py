from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.service.SoundBoardService import SoundBoardService
from main.service.MusicService import MusicService
from main.service.RandomizeTrackService import RandomizeTrackService
from main.domain.public.decorator.detectBan import detect_ban
from main.domain.public.decorator.reportingContent import add_reporting_btn
from django.template.response import TemplateResponse
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from django.views.decorators.http import require_http_methods
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.public.service.ReportContentService import ReportContentService
from main.service.SharedSoundboardService import SharedSoundboardService
from main.domain.common.utils.url import redirection_url
from main.domain.common.repository.UserFavoritePublicSoundboardRepository import UserFavoritePublicSoundboardRepository
from main.domain.common.repository.SoundBoardRepository import SoundBoardRepository
from main.domain.common.utils.logger import logger
from main.domain.common.utils.ServerNotificationBuilder import ServerNotificationBuilder
from main.domain.common.repository.TrackRepository import TrackRepository
from main.domain.common.utils.cache.CacheFactory import CacheFactory


from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper
from main.domain.common.repository.TagRepository import TagRepository

@require_http_methods(['GET'])
def public_index(request):
    return redirect('publicListingSoundboard')

@require_http_methods(['GET'])
@add_reporting_btn()
def public_listing_soundboard(request):
    tag_repository = TagRepository()
    page_number = int(request.GET.get('page', 1))
    selected_tag = request.GET.get('tag', None)
    
    # Filtrage par tag si spécifié
    queryset = SoundBoardRepository().get_search_public_queryset(selected_tag)
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)


    context['listTags'] = tag_repository.get_tag_with_count()
    context['listFavorite'] = UserFavoritePublicSoundboardRepository().get_list_uuids(request.user)
    context['selected_tag'] = selected_tag
    return TemplateResponse(request, 'Html/Public/listing_soundboard.html', context)

@require_http_methods(['GET'])
@login_required
def public_favorite(request):
    page_number = int(request.GET.get('page', 1))
    
    queryset = SoundBoardRepository().get_favorite_public_queryset(request.user)
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['listFavorite'] = UserFavoritePublicSoundboardRepository().get_list_uuids(request.user)
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
def public_music_stream(request, soundboard_uuid, playlist_uuid) ->  HttpResponse|JsonResponse:
    cache = CacheFactory.get_default_cache()
    cache_key = f"musicStream:{request.session.session_key}:{soundboard_uuid}:{playlist_uuid}:{request.GET.get('i','0')}"
    
    try:
        if request.headers.get('X-Metadata-Only') == 'true':
            track_id = cache.get(cache_key)
            if track_id :
                track = TrackRepository().get(track_id, playlist_uuid)
                if track:
                    ret = JsonResponse({"duration":  track.get_duration()}, status=200)
        else:
            track = (RandomizeTrackService(request)).generate_public(soundboard_uuid, playlist_uuid)
            if track:
                # Utilisation du service de soundboard partagé pour gérer le stream
                SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, track)
                cache.set(cache_key, track.id, timeout=20)
                ret = track.get_reponse_content()
        if ret:
            return ret
    except Exception as e:
        logger.error(f"Error in public_music_stream: {e}")
    return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)


@login_required
@require_http_methods(['POST', 'DELETE'])
def favorite_update(request, soundboard_uuid) -> JsonResponse:
    soundboard = SoundBoardRepository().get(soundboard_uuid)
    if not soundboard:
        return JsonResponse({"error": "SoundBoard introuvable."}, status=404)
    
    if request.method == 'POST':
        try:
            UserFavoritePublicSoundboardRepository().get_or_create(user=request.user, uuid_soundboard=soundboard)
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



    