import logging
import random
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from home.models.SoundBoard import SoundBoard
from home.models.Playlist import Playlist
from home.models.Music import Music
from home.manager.SoundBoardPlaylistManager import SoundBoardPlaylistManager
from home.service.SoundBoardService import SoundBoardService
from home.service.PlaylistService import PlaylistService
from home.service.MusicService import MusicService
from home.forms.SoundBoardForm import SoundBoardForm
from home.forms.PlaylistForm import PlaylistForm
from home.forms.MusicForm import MusicForm
from home.filters.SoundBoardFilter import SoundBoardFilter
from home.enum.PermissionEnum import PermissionEnum


@login_required
def soundboard_list(request):
    try:
        _query_set = SoundBoard.objects.all().order_by('id')
        _filter = SoundBoardFilter(queryset=_query_set)
        soundboards = _filter.filter_by_user(request.user)
    except Exception:
        soundboards = []

    
    return render(request, 'Soundboard/soundboard_list.html', {'soundboards': soundboards})

@login_required
@require_http_methods(['POST', 'GET'])
def soundboard_create(request):
    if request.method == 'POST':
        (SoundBoardService(request)).save_form()
        return redirect('soundboardsList')
    else:
        form = SoundBoardForm()
    return render(request, 'Soundboard/soundboard_form.html', {'form': form , 'method' : 'create'})

@login_required
def soundboard_read(request, soundboard_id):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_id)
    if not soundboard :
        return render(request, '404.html', status=404)
    else:   
        return render(request, 'Soundboard/soundboard_read.html', {'soundboard': soundboard})

@login_required
@require_http_methods(['POST', 'GET'])
def soundboard_update(request, soundboard_id):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_id)
    if request.method == 'POST':
        if not soundboard:
            return render(request, '404.html', status=404)
        else:
            form = SoundBoardForm(request.POST, request.FILES, instance=soundboard)
            if form.is_valid():
                form.save()
                return redirect('soundboardsList')
    else:
        if not soundboard:
            return render(request, '404.html', status=404) 
        else:
            form = SoundBoardForm(instance=soundboard)
    return render(request, 'Soundboard/soundboard_form.html', {'form': form, 'method' : 'update'})

@login_required
def soundboard_delete(request, soundboard_id) -> JsonResponse:
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_id)
    if request.method == 'POST':
        if not soundboard:
            return JsonResponse({"error": "SoundBoard introuvable."}, status=404)
        else :
            soundboard.delete()
            return JsonResponse({'success': 'Suppression réussie'}, status=200)
    return JsonResponse({"error": "Méthode non supportée."}, status=405)


@login_required
def soundboard_organize(request, soundboard_id):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_id)
    if not soundboard:
        return render(request, '404.html', status=404)
    
    soundboard_manager = SoundBoardPlaylistManager(request, soundboard)
    return render(request, 'Soundboard/soundboard_organize.html', {'soundboard': soundboard, 'actualPlaylist': soundboard_manager.get_playlists, 'unassociatedPlaylists': soundboard_manager.get_unassociated_playlists})


@login_required
@require_http_methods(['POST', 'DELETE'])
def soundboard_organize_update(request, soundboard_id) -> HttpResponse:
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            soundboard = (SoundBoardService(request)).get_soundboard(soundboard_id)
            data = json.loads(request.body.decode('utf-8'))
            playlist = (PlaylistService(request)).get_playlist(data['idPlaylist'])
            if not playlist:
                raise exceptions.ObjectDoesNotExist
            if request.method == 'POST':
                    soundboard.playlists.add(playlist)
                    soundboard.save()
                    return JsonResponse({'success': 'playslist added'}, status=200)
            if request.method == 'DELETE':
                    soundboard.playlists.remove(playlist)
                    soundboard.save()
                    return JsonResponse({'success': 'playslist deleted'}, status=200)
        except Exception:
            return JsonResponse({"error": "playslist non trouvé."}, status=404)
    return JsonResponse({"error": "Méthode non supportée."}, status=405)
    

@login_required
def playlist_read_all(request):
    playlists = (PlaylistService(request)).get_all_playlist()
    return render(request, 'Playlist/playlist_read_all.html', {'playlists': playlists})

@login_required
def playlist_create_with_soundboard(request, soundboard_id):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_id)
    if(soundboard) : 
        if request.method == 'POST':
            playlist = (PlaylistService(request)).save_form()
            if(playlist):
                soundboard.playlists.add(playlist)
            return redirect('soundboardsRead', soundboard_id=soundboard.id)
        else:
            form = PlaylistForm()
        return render(request, 'Playlist/playlist_create.html', {'form': form , 'method' : 'create', 'listMusic':None})
    return render(request, '404.html', status=404) 

@login_required
def playlist_create(request):
    if request.method == 'POST':
        (PlaylistService(request)).save_form()
        return redirect('playlistsAllList')
    else:
        form = PlaylistForm()
    return render(request, 'Playlist/playlist_create.html', {'form': form , 'method' : 'create', 'listMusic': None})


@login_required
def playlist_update(request, playlist_id):
    playlist = (PlaylistService(request)).get_playlist(playlist_id)
    if request.method == 'POST':
        if not playlist:
            return render(request, '404.html', status=404)
        else:
            form = PlaylistForm(request.POST, request.FILES, instance=playlist)
            if form.is_valid():
                form.save()
                return redirect('playlistsAllList')
    else:
        if not playlist:
            return render(request, '404.html', status=404) 
        else:
            form = PlaylistForm(instance=playlist)
    list_music = (MusicService(request)).get_list_music(playlist_id)
    return render(request, 'Playlist/playlist_create.html', {'form': form, 'method' : 'update', 'listMusic' : list_music})

@login_required
@require_http_methods(['DELETE'])
def playlist_delete(request, playlist_id) -> JsonResponse:
    if request.method == 'DELETE':
        playlist = (PlaylistService(request)).get_playlist(playlist_id)
        if not playlist:
            return JsonResponse({"error": "Playlist introuvable."}, status=404)
        else :
            playlist.delete()
            return JsonResponse({'success': 'Suppression réussie'}, status=200)
    return JsonResponse({"error": "Méthode non supportée."}, status=405)
    
@login_required
@require_http_methods(['POST', 'GET'])
def music_create(request, playlist_id) -> JsonResponse:
    playlist = (PlaylistService(request)).get_playlist(playlist_id)
    if(playlist) : 
        if request.method == 'POST':
            (MusicService(request)).save_form(playlist)
            return redirect('playlistUpdate', playlist_id=playlist_id)
        else:
            form = MusicForm()
        return render(request, 'Music/add_music.html', {'form': form, "playlist":playlist, 'method' : 'create' })
    return render(request, '404.html', status=404) 

@login_required
def music_update(request, playlist_id, music_id):
    playlist = (PlaylistService(request)).get_playlist(playlist_id)
    music = Music.objects.get(id=music_id)
    if not music or not playlist:
        return render(request, '404.html', status=404) 
    if request.method == 'POST':
        form = MusicForm(request.POST, request.FILES, instance=music)
        if form.is_valid():
            form.save()
            return redirect('playlistUpdate', playlist_id=playlist_id)
    else:
        form = MusicForm(instance=music)
    return render(request, 'Music/add_music.html', {'form': form, "playlist":playlist, 'music': music, 'method' : 'update' })



@login_required
@require_http_methods(['DELETE'])
def music_delete(request, playlist_id, music_id) -> JsonResponse:
    if request.method == 'DELETE':
        playlist = (PlaylistService(request)).get_playlist(playlist_id)
        if not playlist:
            return JsonResponse({"error": "Playlist introuvable."}, status=404)
        
        music = Music.objects.get(id=music_id)
        if not music:
            return JsonResponse({"error": "Musique introuvable."}, status=404)
        music.file.delete()
        music.delete()
        return JsonResponse({'success': 'Suppression réussie'}, status=200)
    return JsonResponse({"error": "Méthode non supportée."}, status=405)

@login_required
@require_http_methods(['GET'])
def music_stream(request, playlist_id) -> HttpResponse:
    music = (MusicService(request)).get_random_music(playlist_id)
    if not music :
        return HttpResponse("Musique introuvable.", status=404)
    
    response = HttpResponse(music.file, content_type='audio/*')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(music.fileName)
    return response
    