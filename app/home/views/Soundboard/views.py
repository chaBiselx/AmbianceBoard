import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ...models.SoundBoard import SoundBoard
from ...models.Playlist import Playlist
from ...service.SoundBoardService import SoundBoardService
from ...service.PlaylistService import PlaylistService
from ...forms.SoundBoardForm import SoundBoardForm
from ...forms.PlaylistForm import PlaylistForm
from ...filters.SoundBoardFilter import SoundBoardFilter
from ...filters.PlaylistFilter import PlaylistFilter



@login_required
def soundboard_list(request):
    try:
        _query_Set = SoundBoard.objects.all().order_by('id')
        _filter = SoundBoardFilter(queryset=_query_Set)
        soundboards = _filter.filter_by_user(request.user)
    except:
        soundboards = []

    
    return render(request, 'Soundboard/soundboard_list.html', {'soundboards': soundboards})

@login_required
def soundboard_create(request):
    if request.method == 'POST':
        form = SoundBoardForm(request.POST)
        if form.is_valid():
            soundboard = form.save(commit=False)
            soundboard.user = request.user
            soundboard.save()
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
def soundboard_update(request, soundboard_id):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_id)
    if request.method == 'POST':
        if not soundboard:
            return render(request, '404.html', status=404)
        else:
            form = SoundBoardForm(request.POST, instance=soundboard)
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
def playlist_read_all(request):
    try:
        _query_Set = Playlist.objects.all().order_by('id')
        _filter = PlaylistFilter(queryset=_query_Set)
        playlists = _filter.filter_by_user(request.user)
    except:
        playlists = []
    
    return render(request, 'Playlist/playlist_read_all.html', {'playlists': playlists})

@login_required
def playlist_create_with_soundboard(request, soundboard_id):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_id)
    if(soundboard) : 
        if request.method == 'POST':
            form = PlaylistForm(request.POST)
            if form.is_valid():
                playlist = form.save(commit=False)
                playlist.user = request.user
                playlist.save()
                soundboard.playlists.add(playlist)
                return redirect('soundboardsRead', soundboard_id=soundboard.id)
        else:
            form = PlaylistForm()
        return render(request, 'Playlist/playlist_create.html', {'form': form , 'method' : 'create'})
    return render(request, '404.html', status=404) 

def playlist_create(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            return redirect('playlistsAllList')
    else:
        form = PlaylistForm()
    return render(request, 'Playlist/playlist_create.html', {'form': form , 'method' : 'create'})


def playlist_update(request, playlist_id):
    playlist = (PlaylistService(request)).get_playlist(playlist_id)
    if request.method == 'POST':
        if not playlist:
            return render(request, '404.html', status=404)
        else:
            form = PlaylistForm(request.POST, instance=playlist)
            if form.is_valid():
                form.save()
                return redirect('playlistsAllList')
    else:
        if not playlist:
            return render(request, '404.html', status=404) 
        else:
            form = PlaylistForm(instance=playlist)
    return render(request, 'Playlist/playlist_create.html', {'form': form, 'method' : 'update'})

@login_required
def playlist_delete(request, playlist_id) -> JsonResponse:
    playlist = (PlaylistService(request)).get_playlist(playlist_id)
    if request.method == 'POST':
        if not playlist:
            return JsonResponse({"error": "Playlist introuvable."}, status=404)
        else :
            playlist.delete()
            return JsonResponse({'success': 'Suppression réussie'}, status=200)
    return JsonResponse({"error": "Méthode non supportée."}, status=405)
    