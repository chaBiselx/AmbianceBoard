from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from main.models.Music import Music
from main.service.PlaylistService import PlaylistService
from main.service.MusicService import MusicService
from main.service.MultipleMusicUploadService import MultipleMusicUploadService
from main.forms.MusicForm import MusicForm
from main.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.enum.ErrorMessageEnum import ErrorMessageEnum
from main.enum.MusicFormatEnum import MusicFormatEnum
from main.utils.UserTierManager import UserTierManager
from main.service.LinkService import LinkService
from main.forms.LinkMusicForm import LinkMusicForm


from main.utils.logger import logger

@login_required
@require_http_methods(['POST'])
def upload_multiple_music(request, playlist_uuid) -> JsonResponse:
    """Upload multiple de fichiers musicaux via DragAndDrop"""
    playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
    if not playlist:
        return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
    
    if request.method == 'POST':
        if len(request.FILES) == 0:
            return JsonResponse({"error": "Aucun fichier reçu"}, status=400)

        multiple_music_upload_service = MultipleMusicUploadService(request)
        results, errors = multiple_music_upload_service.process_upload(playlist)

        if errors:
            return JsonResponse({"success": False, "error": errors}, status=400)

        return JsonResponse({"success": True, "uploaded_files": results}, status=200)

    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)

@login_required
@require_http_methods(['POST', 'GET'])
def music_create(request, playlist_uuid):
    """Création d'une nouvelle musique dans une playlist"""
    playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
    if playlist:
        if request.method == 'POST':
            try:
                (MusicService(request)).save_form(playlist)
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('playlistUpdate', playlist_uuid=playlist_uuid)
        else:
            form = MusicForm()
        
        limit = UserTierManager.get_user_limits(request.user)
        nb_music_remaining = limit['music_per_playlist'] - playlist.tracks.count()
        if nb_music_remaining < 0:
            nb_music_remaining = 0
        file_size_mb = limit['weight_music_mb']
        
        return render(request, 'Html/Music/add_music.html', {
            'form': form, 
            "playlist": playlist, 
            'nbMusicRemaining': nb_music_remaining, 
            'file_size_mb': file_size_mb, 
            'MusicFormatEnum': MusicFormatEnum.values()
        })
    return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)


@login_required
@require_http_methods(['GET', 'POST'])
def music_update(request, playlist_uuid, music_id):
    """Mise à jour d'une musique existante"""
    playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
    music = Music.objects.get(id=music_id)
    if not music or not playlist:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    if request.method == 'POST':
        try:
            (MusicService(request)).save_form(playlist, music)
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('playlistUpdate', playlist_uuid=playlist_uuid)
    else:
        form = MusicForm(instance=music)
    
    return render(request, 'Html/Music/update_music.html', {
        'form': form, 
        "playlist": playlist, 
        'music': music
    })


@login_required
@require_http_methods(['DELETE'])
def music_delete(request, playlist_uuid, music_id) -> JsonResponse:
    """Suppression d'une musique"""
    if request.method == 'DELETE':
        playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
        if not playlist:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        
        music = Music.objects.get(id=music_id)
        if not music:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        
        music.file.delete()
        music.delete()
        return JsonResponse({'success': 'Suppression musique réussie'}, status=200)
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)





@login_required
@require_http_methods(['POST', 'GET'])
def link_create(request, playlist_uuid):
    """Création d'un nouveau lien musical dans une playlist"""
    playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
    if not playlist:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    if request.method == 'POST':
        try:
            (LinkService(request)).save_form(playlist)
            messages.success(request, "Lien musical ajouté avec succès!")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('playlistUpdate', playlist_uuid=playlist_uuid)
    else:
        form = LinkMusicForm()
    
    return render(request, 'Html/Music/add_link_music.html', {
        'form': form,
        'playlist': playlist
    })


@login_required
@require_http_methods(['GET', 'POST'])
def link_update(request, playlist_uuid, link_id):
    """Mise à jour d'un lien musical existant"""
    playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
    if not playlist:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)

    link = (LinkService(request)).get_link(link_id)
    if not link:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)

    if request.method == 'POST':
        try:
            (LinkService(request)).save_form(playlist, link)
            messages.success(request, "Lien musical modifié avec succès!")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('playlistUpdate', playlist_uuid=playlist_uuid)
    else:
        form = LinkMusicForm(instance=link)
    
    return render(request, 'Html/Music/update_link_music.html', {
        'form': form,
        'playlist': playlist,
        'link': link
    })


@login_required
@require_http_methods(['DELETE'])
def link_delete(request, playlist_uuid, link_id) -> JsonResponse:
    """Suppression d'un lien musical"""
    if request.method == 'DELETE':
        playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
        if not playlist:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        
        link = (LinkService(request)).get_link(link_id)
        if not link:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

        link.delete()
        return JsonResponse({'success': 'Suppression lien musical réussie'}, status=200)
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)
