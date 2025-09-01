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
from main.architecture.persistence.models.User import User
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from main.domain.common.utils.url import redirection_url
from main.architecture.persistence.models.Tag import Tag
from main.domain.moderator.form.TagForm import TagForm



@login_required
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
@require_http_methods(['GET'])
def moderator_dashboard(request) -> HttpResponse:
    nb_users = User.objects.all().count()
    moy_playlist_per_user = (User.objects.annotate(playlist_count=models.Count('playlist')).aggregate(avg_playlists=Avg('playlist_count')))['avg_playlists']
    moy_music_per_user = User.objects.annotate(
        music_count=models.Count('playlist__tracks')
        ).aggregate(avg_music=Avg('music_count'))['avg_music']
    moy_music_per_playlist = Playlist.objects.annotate(
        music_count=models.Count('tracks')
        ).aggregate(avg_music=Avg('music_count'))['avg_music']
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
    
    queryset = Playlist.objects.all()
    paginator = Paginator(queryset, 50)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_playlist_img.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_images_soundboard(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))

    queryset = SoundBoard.objects.all()
    paginator = Paginator(queryset, 50)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_soundboard_img.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_playlist(request, playlist_uuid) -> HttpResponse:
    playlist = Playlist.objects.get(uuid=playlist_uuid)
    return render(request, 'Html/Moderator/info_playlist.html', {"playlist":playlist})
    
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_soundboard(request, soundboard_uuid) -> HttpResponse:
    soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
    return render(request, 'Html/Moderator/info_soundboard.html', {"soundboard":soundboard})
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_log_moderation(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    
    queryset = UserModerationLog.objects.all().order_by('created_at')
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_log.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_user(request, user_uuid) -> HttpResponse:
    user = User.objects.get(id=user_uuid)
    return render(request, 'Html/Moderator/info_user.html', {"user":user})

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_report(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    queryset = ReportContent.objects.filter(moderator__isnull=True).order_by('created_at')
 
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['archive'] = False
    
    return render(request, 'Html/Moderator/listing_report.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_report_archived(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    queryset = ReportContent.objects.filter(moderator__isnull=False).order_by('created_at')
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    context['archive'] = True
    
    return render(request, 'Html/Moderator/listing_report.html', context)
    
@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_get_infos_report(request, report_id) -> HttpResponse:
    user = ReportContent.objects.get(id=report_id)
    return render(request, 'Html/Moderator/info_content_report.html', {"user":user})


@login_required
@require_http_methods(['POST'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def reporting_add_log(request) -> HttpResponse:
    # info reportContent 
    user = User.objects.get(uuid=request.POST.get('user_id'))
    if user is not None:
        report_content = None
        content_report_accepted = request.POST.get('contentReport_accepted')
        if content_report_accepted:
            id_report_content = request.POST.get('contentReport_id')
            content_moderator_response = request.POST.get('content_moderator_response')
            if id_report_content and content_moderator_response:
                report_content = ReportContent.objects.get(id=id_report_content)
                if report_content is not None:
                    report_content.resultModerator = content_moderator_response
                    report_content.moderator = request.user
                    report_content.dateResultModerator = datetime.now()
                    # report_content.save()
        
        moderator_log_accepted = request.POST.get('moderator_log_accepted')
        if moderator_log_accepted:
            UserModerationLog.objects.create(
                user = user,
                moderator = request.user,
                message = request.POST.get('moderator_log_message'),
                tag = request.POST.get('moderator_log_tag'),
                model = request.POST.get('moderator_log_model', ModerationModelEnum.UNKNOWN.name),
                report = report_content
            )
            
        
        action_ban_user = request.POST.get('action_ban_user')
        if action_ban_user:
            duration_ban = int(request.POST.get('action_ban_duration', '12'))
            if(duration_ban <=0):
                duration_ban = 12
            user.isBan = True
            user.reasonBan = request.POST.get('action_ban_reason')
            user.banExpiration = datetime.now() + timedelta(days=duration_ban * 31)
            user.save()
        
    return redirect(redirection_url(request.POST.get('redirect_uri', 'moderatorDashboard')))

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_tags(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    
    queryset = Tag.objects.all().order_by('name')
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
    tag = Tag.objects.get(uuid=tag_uuid)
    
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
    tag = Tag.objects.get(uuid=tag_uuid)
    return render(request, 'Html/Moderator/info_tag.html', {"tag": tag})
