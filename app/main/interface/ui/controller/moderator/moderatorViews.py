from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import Group, Permission
from django.db.models import Avg, Count
from django.db import models
from django.urls import reverse
from django.core.paginator import Paginator
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.UserModerationLog import UserModerationLog
from main.architecture.persistence.models.ReportContent import ReportContent
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.enum.ModerationModelEnum import ModerationModelEnum
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from django.utils import timezone
from main.domain.common.utils.url import redirection_url
from main.interface.ui.forms.moderator.TagForm import TagForm
from main.interface.ui.forms.moderator.PlaylistTagForm import PlaylistTagForm
from main.architecture.persistence.repository.UserRepository import UserRepository
from main.architecture.persistence.repository.PlaylistRepository import PlaylistRepository
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.architecture.persistence.repository.UserModerationLogRepository import UserModerationLogRepository
from main.architecture.persistence.repository.ReportContentRepository import ReportContentRepository
from main.domain.moderator.service.TreatmentReportService import TreatmentReportService
from main.domain.moderator.dto.TreatmentReportDto import TreatmentReportDto
from main.architecture.persistence.repository.TagRepository import TagRepository
from main.architecture.persistence.repository.PlaylistTagRepository import PlaylistTagRepository
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.ChartPeriodEnum import ChartPeriodEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.moderator.service.ModeratorSoundboardStatsService import ModeratorSoundboardStatsService




@login_required
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
@require_http_methods(['GET'])
def moderator_dashboard(request) -> HttpResponse:
    user_repository = UserRepository()
    playlist_repository = PlaylistRepository()
    nb_users = user_repository.get_stats_nb_user()
    moy_playlist_per_user = user_repository.get_stats_avg_playlist_per_user()
    moy_music_per_user = user_repository.get_stats_avg_track_per_user() 
    moy_music_per_playlist = playlist_repository.get_stat_nb_track_per_playlist()
    
    return render(request, 'Html/Moderator/dashboard.html', {
            'nb_users': nb_users, 
            'moy_playlist_per_user': moy_playlist_per_user, 
            'moy_music_per_user': moy_music_per_user, 
            'moy_music_per_playlist': moy_music_per_playlist
    })
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_images_playlist(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    
    queryset = PlaylistRepository().get_all_queryset()
    paginator = Paginator(queryset, 50)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_playlist_img.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_images_soundboard(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))

    queryset = SoundBoardRepository().get_all_queryset()
    paginator = Paginator(queryset, 200)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_soundboard_img.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_playlist(request, playlist_uuid) -> HttpResponse:
    playlist = PlaylistRepository().get(playlist_uuid)
    return render(request, 'Html/Moderator/info_playlist.html', {"playlist":playlist})
    
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_soundboard(request, soundboard_uuid) -> HttpResponse:
    soundboard = SoundBoardRepository().get(soundboard_uuid)
    return render(request, 'Html/Moderator/info_soundboard.html', {"soundboard":soundboard})


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_soundboard_listening_time_stats(request, soundboard_uuid) -> JsonResponse:
    try:
        period = request.GET.get('period', ChartPeriodEnum.get_default_period())
        if not ChartPeriodEnum.is_valid_period(period):
            period = ChartPeriodEnum.get_default_period()

        days = int(period)
        end_dt = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_dt = end_dt - timedelta(days=days - 1)

        soundboard = SoundBoardRepository().get(soundboard_uuid)
        if not soundboard:
            raise ValueError("Soundboard non trouvée")

        response_data = ModeratorSoundboardStatsService().get_soundboard_listening_time_data(soundboard, start_dt, end_dt)
        return JsonResponse({
            'title': f"Temps d'écoute soundboard - {days} jours",
            'x_label': 'Date',
            'y_label': 'Temps (min)',
            'data': response_data,
        })
    except Exception as e:
        return JsonResponse({
            'error': ErrorMessageEnum.DATA_RECUPERATION,
            'message': str(e)
        }, status=500)
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_log_moderation(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))

    queryset = UserModerationLogRepository().get_all_queryset()
    paginator = Paginator(queryset, 200)
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_log.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_user(request, user_uuid) -> HttpResponse:
    user_repository = UserRepository()
    user = user_repository.get_user(user_uuid)
    return render(request, 'Html/Moderator/info_user.html', {"user":user})

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_report(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    queryset = ReportContentRepository().get_all_queryset(archived=False)
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['archive'] = False
    
    return render(request, 'Html/Moderator/listing_report.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_report_archived(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    queryset = ReportContentRepository().get_all_queryset(archived=True)
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['archive'] = True
    
    return render(request, 'Html/Moderator/listing_report.html', context)
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_report(request, report_id) -> HttpResponse:
    content_report = ReportContentRepository().get(report_id)
    if not content_report:
        return render(request,  HtmlDefaultPageEnum.ERROR_404.value, status=404)
    return render(request, 'Html/Moderator/info_content_report.html', {"content_report":content_report})


@login_required
@require_http_methods(['POST'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def reporting_add_log(request) -> HttpResponse:
    # info reportContent 
    user_repository = UserRepository()
    user = user_repository.get_user(request.POST.get('user_id'))
    if user is not None:
        dto = TreatmentReportDto.from_request(request)
        treatment_report_service = TreatmentReportService(dto, user, request.user)
        treatment_report_service.update_content_report()
        treatment_report_service.create_log_moderation()
        treatment_report_service.action_ban()
        treatment_report_service.action_ban_playlist_copie()

    return redirect(redirection_url(request.POST.get('redirect_uri', 'moderatorDashboard')))

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_tags(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    
    tag_repository = TagRepository()
    queryset = tag_repository.get_all_queryset()
    paginator = Paginator(queryset, 50)  
    context = extract_context_to_paginator(paginator, page_number)
    context['title'] = 'Gestion des tags'
    return render(request, 'Html/Moderator/listing_tags.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_create_tag(request) -> HttpResponse:
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('moderatorListingTags')
    else:
        form = TagForm()
    
    return render(request, 'Html/Moderator/create_tag.html', {'form': form})

@login_required
@require_http_methods(['GET', 'POST'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_edit_tag(request, tag_uuid) -> HttpResponse:
    tag_repository = TagRepository()
    tag = tag_repository.get_with_uuid(uuid=tag_uuid)

    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('moderatorListingTags')
    else:
        form = TagForm(instance=tag)
    
    return render(request, 'Html/Moderator/edit_tag.html', {'form': form, 'tag': tag})


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_tag(request, tag_uuid) -> HttpResponse:
    tag_repository = TagRepository()
    tag = tag_repository.get_with_uuid(uuid=tag_uuid)
    if tag:
        return render(request, 'Html/Moderator/info_tag.html', {"tag": tag})
    else : 
        return render(request,  HtmlDefaultPageEnum.ERROR_404.value, status=404)


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_playlist_tags(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))

    playlist_tag_repository = PlaylistTagRepository()
    queryset = playlist_tag_repository.get_all_queryset()
    paginator = Paginator(queryset, 50)
    context = extract_context_to_paginator(paginator, page_number)
    context['title'] = 'Gestion des tags playlist'
    return render(request, 'Html/Moderator/playlist_tag/listing_playlist_tags.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_manage_playlist_tag(request, playlist_tag_label=None) -> HttpResponse:
    is_edit = playlist_tag_label is not None
    playlist_tag = None

    if is_edit:
        playlist_tag = PlaylistTagRepository().get_with_label(label=playlist_tag_label)
        if not playlist_tag:
            return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)

    if request.method == 'POST':
        form = PlaylistTagForm(request.POST, instance=playlist_tag)
        if form.is_valid():
            form.save()
            return redirect('moderatorListingPlaylistTags')
    else:
        form = PlaylistTagForm(instance=playlist_tag)

    return render(
        request,
        'Html/Moderator/playlist_tag/create_playlist_tag.html',
        {
            'form': form,
            'is_edit': is_edit,
            'playlist_tag': playlist_tag,
        },
    )
    

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_playlist_tag(request, playlist_tag_label) -> HttpResponse:
    playlist_tag_repository = PlaylistTagRepository()
    playlist_tag = playlist_tag_repository.get_with_label(label=playlist_tag_label)
    if playlist_tag:
        return render(request, 'Html/Moderator/playlist_tag/info_playlist_tag.html', {'playlist_tag': playlist_tag})
    return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_playlist_list_for_playlist_tag(request) -> HttpResponse:
    selected_tag = request.GET.get('tag', None)
    page_number = int(request.GET.get('page', 1))
    playlist_repository = PlaylistRepository()
    
    if selected_tag == 'empty':
        queryset = playlist_repository.get_all_without_playlist_tag_queryset()
    elif selected_tag:
        playlist_tag_repository = PlaylistTagRepository()
        playlist_tag = playlist_tag_repository.get_with_label(label=selected_tag)
        if not playlist_tag:
            return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
        queryset = playlist_repository.get_listing_playlist_queryset_with_tag(PlaylistTag=playlist_tag, filter={})
    else: 
        queryset = playlist_repository.get_all_queryset() 
    
    paginator = Paginator(queryset, 50)
    context = extract_context_to_paginator(paginator, page_number)
    context['title'] = 'Playlists sans tag'
    
    playlist_tag_repository = PlaylistTagRepository()
    context['list_tag'] = playlist_tag_repository.get_all()   
    context['selected_tag'] = selected_tag 
    return render(request, 'Html/Moderator/playlist_tag/listing_playlist_to_associate.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_popup_playlist_tag(request, playlist_uuid) -> HttpResponse:
    if playlist_uuid:
        playlist = PlaylistRepository().get(playlist_uuid)
        if not playlist:
            return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    playlist_tag_repository = PlaylistTagRepository()
    list_tag = playlist_tag_repository.get_all()   
    url_update = reverse('moderatorPostPopupPlaylistTag', kwargs={'playlist_uuid': playlist_uuid})         

    return render(request, 'Html/Moderator/playlist_tag/popup_playlist_tag_update.html', {'playlist': playlist, 'list_tag': list_tag, 'url_update': url_update})


@login_required
@require_http_methods(['POST'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_post_popup_playlist_tag(request, playlist_uuid) -> JsonResponse:
    playlist_tag_label = request.POST.get('playlist_tag_label')
    action = request.POST.get('action')
    playlist = PlaylistRepository().get(playlist_uuid)
    playlist_tag = PlaylistTagRepository().get_with_label(label=playlist_tag_label)
    if playlist and playlist_tag:
        if action == 'add':
            playlist.playlist_tags.add(playlist_tag)
            return JsonResponse({'status': 'success', 'message': f'Tag "{playlist_tag_label}" ajouté à la playlist.'})
        elif action == 'remove':
            playlist.playlist_tags.remove(playlist_tag)
            return JsonResponse({'status': 'success', 'message': f'Tag "{playlist_tag_label}" retiré de la playlist.'})
    return JsonResponse({'status': 'error', 'message': 'Action invalide ou données manquantes.'}, status=400)