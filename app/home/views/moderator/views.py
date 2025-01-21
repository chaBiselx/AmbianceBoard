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
from home.enum.PermissionEnum import PermissionEnum
from home.models.User import User
from home.utils.ExtractPaginator import extract_context_to_paginator


@login_required
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_dashboard(request) -> HttpResponse:
    nb_users = User.objects.all().count()
    moy_playlist_per_user = (User.objects.annotate(playlist_count=models.Count('playlist')).aggregate(avg_playlists=Avg('playlist_count')))['avg_playlists']
    moy_music_per_user = (User.objects.annotate(music_count=Count('playlist__music')).aggregate(avg_music=Avg('music_count')))['avg_music']
    moy_music_per_playlist = (Playlist.objects.annotate(music_count=models.Count('music')).aggregate(avg_musics=Avg('music_count')))['avg_musics']

    return render(request, 'Moderator/dashboard.html', {
            'nb_users': nb_users, 
            'moy_playlist_per_user': moy_playlist_per_user, 
            'moy_music_per_user': moy_music_per_user, 
            'moy_music_per_playlist': moy_music_per_playlist
    })
    
@login_required
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_images_playlist(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 50))
    
    queryset = Playlist.objects.exclude(icon__isnull=False, icon__exact='')
    paginator = Paginator(queryset, 1)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Moderator/listing_playlist_img.html', context)

@login_required
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name, login_url='login')
def moderator_listing_images_soundboard(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 50))
    
    queryset = SoundBoard.objects.exclude(icon__isnull=False, icon__exact='')
    paginator = Paginator(queryset, 1)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Moderator/listing_soundboard_img.html', context)