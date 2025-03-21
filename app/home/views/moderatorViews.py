import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import Group, Permission
from django.db.models import Avg, Count
from django.db import models
from django.core.paginator import Paginator
from home.models.Playlist import Playlist
from home.models.SoundBoard import SoundBoard
from home.models.UserModerationLog import UserModerationLog
from home.enum.PermissionEnum import PermissionEnum
from home.models.User import User
from home.utils.ExtractPaginator import extract_context_to_paginator
from django.views.decorators.http import require_http_methods


@login_required
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
@require_http_methods(['GET'])
def moderator_dashboard(request) -> HttpResponse:
    nb_users = User.objects.all().count()
    moy_playlist_per_user = (User.objects.annotate(playlist_count=models.Count('playlist')).aggregate(avg_playlists=Avg('playlist_count')))['avg_playlists']
    moy_music_per_user = (User.objects.annotate(music_count=Count('playlist__music')).aggregate(avg_music=Avg('music_count')))['avg_music']
    moy_music_per_playlist = (Playlist.objects.annotate(music_count=models.Count('music')).aggregate(avg_musics=Avg('music_count')))['avg_musics']

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
    
    queryset = Playlist.objects.exclude(icon__isnull=False, icon__exact='')
    paginator = Paginator(queryset, 50)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Moderator/listing_playlist_img.html', context)

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_images_soundboard(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))

    queryset = SoundBoard.objects.exclude(icon__isnull=False, icon__exact='')
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
def moderator_get_infos_soundboard(request, soundboard_uuid) -> HttpResponse:
    soundboard = SoundBoard.objects.get(uuid=soundboard_uuid)
    return render(request, 'Html/Moderator/info_soundboard.html', {"soundboard":soundboard})

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_log_moderation(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 50))
    
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
    
    