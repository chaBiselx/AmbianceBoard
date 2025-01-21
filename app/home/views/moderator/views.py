import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import Group, Permission
from django.db.models import Avg, Count
from django.db import models
from home.models.Playlist import Playlist
from home.enum.PermissionEnum import PermissionEnum
from home.models.User import User


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
    
