from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import Group, Permission
from django.db.models import Avg, Count
from django.db import models
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
from main.domain.common.utils.url import redirection_url
from main.domain.moderator.form.TagForm import TagForm
from main.domain.common.repository.UserRepository import UserRepository
from main.domain.common.repository.PlaylistRepository import PlaylistRepository
from main.domain.moderator.service.TreatmentReportService import TreatmentReportService
from main.domain.moderator.dto.TreatmentReportDto import TreatmentReportDto
from main.domain.common.repository.TagRepository import TagRepository
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum




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
    
    queryset = Playlist.objects.all()  #TODO repository
    paginator = Paginator(queryset, 50)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_playlist_img.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_images_soundboard(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))

    queryset = SoundBoard.objects.all()  #TODO repository
    paginator = Paginator(queryset, 50)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_soundboard_img.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_playlist(request, playlist_uuid) -> HttpResponse:
    playlist = Playlist.objects.get(uuid=playlist_uuid)  #TODO repository
    return render(request, 'Html/Moderator/info_playlist.html', {"playlist":playlist})
    
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_soundboard(request, soundboard_uuid) -> HttpResponse:
    soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)  #TODO repository
    return render(request, 'Html/Moderator/info_soundboard.html', {"soundboard":soundboard})
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_log_moderation(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    
    queryset = UserModerationLog.objects.all().order_by('created_at')  #TODO repository
    paginator = Paginator(queryset, 100)  
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
    queryset = ReportContent.objects.filter(moderator__isnull=True).order_by('created_at')  #TODO repository
 
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['archive'] = False
    
    return render(request, 'Html/Moderator/listing_report.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_report_archived(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    queryset = ReportContent.objects.filter(moderator__isnull=False).order_by('created_at')  #TODO repository
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['archive'] = True
    
    return render(request, 'Html/Moderator/listing_report.html', context)
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_report(request, report_id) -> HttpResponse:
    content_report = ReportContent.objects.get(id=report_id)  #TODO repository
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
