import logging
import random
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from home.models.SoundBoard import SoundBoard
from home.models.Playlist import Playlist
from home.models.Music import Music
from home.manager.SoundBoardPlaylistManager import SoundBoardPlaylistManager
from home.service.SoundBoardService import SoundBoardService
from home.service.PlaylistService import PlaylistService
from home.service.MusicService import MusicService
from home.service.LinkService import LinkService
from home.service.SoundboardPlaylistService import SoundboardPlaylistService
from home.service.MultipleMusicUploadService import MultipleMusicUploadService
from home.forms.SoundBoardForm import SoundBoardForm
from home.forms.PlaylistForm import PlaylistForm
from home.forms.MusicForm import MusicForm
from home.forms.LinkMusicForm import LinkMusicForm
from home.filters.SoundBoardFilter import SoundBoardFilter
from home.enum.PermissionEnum import PermissionEnum
from home.enum.PlaylistTypeEnum import PlaylistTypeEnum
from home.enum.ConfigTypeDataEnum import ConfigTypeDataEnum
from home.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from home.formatter.TypePlaylistFormater import TypePlaylistFormater
from home.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from home.enum.ErrorMessageEnum import ErrorMessageEnum
from home.service.SharedSoundboardService import SharedSoundboardService
from home.enum.MusicFormatEnum import MusicFormatEnum
from home.enum.LinkMusicAllowedEnum import LinkMusicAllowedEnum
from home.utils.UserTierManager import UserTierManager

logger = logging.getLogger('home')


@login_required
@require_http_methods(['GET'])
def soundboard_list(request):
    try:
        _query_set = SoundBoard.objects.all().order_by('uuid')
        _filter = SoundBoardFilter(queryset=_query_set)
        soundboards = _filter.filter_by_user(request.user)
    except Exception:
        soundboards = []

    
    return render(request, 'Html/Soundboard/soundboard_list.html', {'soundboards': soundboards})

@login_required
@require_http_methods(['POST', 'GET'])
def soundboard_create(request):
    if request.method == 'POST':
        (SoundBoardService(request)).save_form()
        return redirect('soundboardsList')
    else:
        form = SoundBoardForm()
    return render(request, 'Html/Soundboard/soundboard_form.html', {'form': form , 'method' : 'create'})

@login_required
@require_http_methods(['GET'])
def soundboard_read(request, soundboard_uuid):
    SharedSoundboardService(request, soundboard_uuid).music_stop_all()
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard :
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    else:   
        return render(request, 'Html/Soundboard/soundboard_read.html', {'soundboard': soundboard, 'PlaylistTypeEnum' : list(PlaylistTypeEnum) })

@login_required
@require_http_methods(['POST', 'GET'])
def soundboard_update(request, soundboard_uuid):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if request.method == 'POST':
        if not soundboard:
            return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
        else:
            form = SoundBoardForm(request.POST, request.FILES, instance=soundboard)
            if form.is_valid():
                form.save()
                return redirect('soundboardsList')
    else:
        if not soundboard:
            return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404) 
        else:
            form = SoundBoardForm(instance=soundboard)
    return render(request, 'Html/Soundboard/soundboard_form.html', {'form': form, 'method' : 'update'})

@login_required
@require_http_methods(['DELETE'])
def soundboard_delete(request, soundboard_uuid) -> JsonResponse:
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if request.method == 'DELETE':
        if not soundboard:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        else :
            soundboard.delete()
            return JsonResponse({'success': 'Suppression soundboard réussie'}, status=200)
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)


@login_required
@require_http_methods(['GET'])
def soundboard_organize(request, soundboard_uuid):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    soundboard_manager = SoundBoardPlaylistManager(request, soundboard)
    return render(request, 'Html/Soundboard/soundboard_organize.html', {'soundboard': soundboard, 'actualPlaylist': soundboard_manager.get_playlists, 'unassociatedPlaylists': soundboard_manager.get_unassociated_playlists})


@login_required
@require_http_methods(['POST', 'DELETE', 'UPDATE'])
def soundboard_organize_update(request, soundboard_uuid) -> HttpResponse:
    try:
        soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
        data = json.loads(request.body.decode('utf-8'))
        playlist = (PlaylistService(request)).get_playlist(data['idPlaylist'])
        new_order = None
        if 'newOrder' in data.keys():
            if(data['newOrder'] is None):
                new_order = 1
            else :
                new_order = int(data['newOrder'])
        soundboard_playlist_service = SoundboardPlaylistService(soundboard)
        if not playlist:
            raise exceptions.ObjectDoesNotExist
        if request.method == 'POST':
            
            soundboard_playlist_service.add(playlist, new_order)
            return JsonResponse({'success': 'playlist added', 'order': playlist.get_order()}, status=200)
        if request.method == 'UPDATE':
            soundboard_playlist_service.update(playlist, new_order)
            return JsonResponse({'success': 'playslist added', 'order': playlist.get_order()}, status=200)
        if request.method == 'DELETE':
            soundboard_playlist_service.remove(playlist)
            return JsonResponse({'success': 'playslist deleted'}, status=200)
    except Exception as e:
        logger.error(f"soundboard_organize_update : {e}")
        return JsonResponse({"error": "playslist non trouvé."}, status=404)
    

@login_required
@require_http_methods(['GET'])
def playlist_read_all(request):
    playlists = (PlaylistService(request)).get_all_playlist()
    return render(request, 'Html/Playlist/playlist_read_all.html', {'playlists': playlists})

@login_required
@require_http_methods(['GET', 'POST'])
def playlist_create_with_soundboard(request, soundboard_uuid):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if(soundboard) : 
        if request.method == 'POST':
            playlist = (PlaylistService(request)).save_form()
            if(playlist):
                soundboard.playlists.add(playlist)
            return redirect('soundboardsRead', soundboard_uuid=soundboard.uuid)
        else:
            form = PlaylistForm()
        list_default_color = DefaultColorPlaylistService(request.user).get_list_default_color()
        link_music_allowed_values = [choice.value for choice in LinkMusicAllowedEnum]
        return render(
            request, 
            'Html/Playlist/playlist_create.html', # NOSONAR
            {'form': form , 'method' : 'create', 'listMusic':None, 'list_default_color': list_default_color, 'LinkMusicAllowedEnum': link_music_allowed_values}
        )
    return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404) 

@login_required
@require_http_methods(['GET', 'POST'])
def playlist_create(request):
    if request.method == 'POST':
        playlist = (PlaylistService(request)).save_form()
        return redirect('playlistUpdate', playlist_uuid=playlist.uuid)
    else:
        form = PlaylistForm()
    list_default_color = DefaultColorPlaylistService(request.user).get_list_default_color()
    link_music_allowed_values = [choice.value for choice in LinkMusicAllowedEnum]
    return render(
        request,
        'Html/Playlist/playlist_create.html', # NOSONAR
        {'form': form , 'method' : 'create', 'listMusic': None, 'list_default_color': list_default_color,'LinkMusicAllowedEnum': link_music_allowed_values}
    )

@login_required
@require_http_methods(['GET'])
def playlist_describe_type(request)-> HttpResponse:
    data = []
    for type_playlist in PlaylistTypeEnum:
        obj = {
            "type": type_playlist.name, 
            "name": type_playlist.value,
            "structure": TypePlaylistFormater(type_playlist).get_structured_data()
        }
        data.append(obj)
    list_param ={
        ConfigTypeDataEnum.STATIC.name : {
            'name' : ConfigTypeDataEnum.STATIC.name,
            'value' : ConfigTypeDataEnum.STATIC.value,
            'class' : ConfigTypeDataEnum.STATIC.get_icon_class(),
        },
        ConfigTypeDataEnum.PARAM.name :{
            'name' : ConfigTypeDataEnum.PARAM.name,
            'value' : ConfigTypeDataEnum.PARAM.value,
            'class' : ConfigTypeDataEnum.PARAM.get_icon_class(),
        },
        ConfigTypeDataEnum.PARAM_WITH_DEFAULT.name : {
            'name' : ConfigTypeDataEnum.PARAM_WITH_DEFAULT.name,
            'value' : ConfigTypeDataEnum.PARAM_WITH_DEFAULT.value,
            'class' : ConfigTypeDataEnum.PARAM_WITH_DEFAULT.get_icon_class(),
        }
    }
    
    return render(request, 'Html/Playlist/describe_type.html', {'dataFacade': data, "listParam":list_param})
    
    

@login_required
@require_http_methods(['GET'])
def playlist_listing_colors(request) -> JsonResponse:
    default_playlists = DefaultColorPlaylistService(request.user).get_list_default_color_ajax()
    

    
    unique_playlists = Playlist.objects.values('colorText', 'color', 'typePlaylist').distinct().all()
    for playlist in unique_playlists:
        playlist['typePlaylist'] = PlaylistTypeEnum[playlist['typePlaylist']].value
    return JsonResponse({"unique_playlists": list(unique_playlists), "default_playlists": list(default_playlists)}, status=200)


@login_required
@require_http_methods(['GET', 'POST'])
def playlist_update(request, playlist_uuid):
    playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
    if not playlist:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    if request.method == 'POST':
        form = PlaylistForm(request.POST, request.FILES, instance=playlist)
        if form.is_valid():
            form.save()
            return redirect('playlistUpdate', playlist_uuid=playlist_uuid)
    else:
        form = PlaylistForm(instance=playlist)
    list_track = (MusicService(request)).get_list_music(playlist_uuid)
    list_default_color = DefaultColorPlaylistService(request.user).get_list_default_color()
    link_music_allowed_values = [choice.value for choice in LinkMusicAllowedEnum]
    return render(
        request, 
        'Html/Playlist/playlist_create.html', # NOSONAR
        {'form': form, 'method' : 'update', 'listTrack' : list_track, 'list_default_color':list_default_color, 'LinkMusicAllowedEnum': link_music_allowed_values}
    )
    
@login_required
@require_http_methods(['GET'])
def playlist_create_track_stream(request, playlist_uuid, music_id) -> HttpResponse|StreamingHttpResponse:
    track = (MusicService(request)).get_specific_music(playlist_uuid, music_id)
    if not track :
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    
    ret = track.get_reponse_content()
    if ret is None:
        return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)
    return ret


@login_required
@require_http_methods(['DELETE'])
def playlist_delete(request, playlist_uuid) -> JsonResponse:
    if request.method == 'DELETE':
        playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
        if not playlist:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        else :
            playlist.delete()
            return JsonResponse({'success': 'Suppression playlist réussie'}, status=200)
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)
    
@login_required
@require_http_methods(['POST', 'GET'])
def music_create(request, playlist_uuid) -> JsonResponse:
    playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
    if(playlist) : 
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
        return render(request, 'Html/Music/add_music.html', {'form': form, "playlist":playlist , 'nbMusicRemaining' : nb_music_remaining , 'file_size_mb': file_size_mb, 'MusicFormatEnum': [ext.value for ext in MusicFormatEnum]})
    return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404) 

@login_required
@require_http_methods(['GET', 'POST'])
def music_update(request, playlist_uuid, music_id):
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
    return render(request, 'Html/Music/update_music.html', {'form': form, "playlist":playlist, 'music': music })



@login_required
@require_http_methods(['DELETE'])
def music_delete(request, playlist_uuid, music_id) -> JsonResponse:
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
@require_http_methods(['GET'])
def music_stream(request, soundboard_uuid, playlist_uuid) -> HttpResponse:
    track = (MusicService(request)).get_random_music(playlist_uuid)
    if not track :
        return HttpResponse(ErrorMessageEnum.ELEMENT_NOT_FOUND.value, status=404)
    
    SharedSoundboardService(request, soundboard_uuid).music_start(playlist_uuid, track)

    try:
        response = track.get_reponse_content()
        if response:
            return response
    except Exception as e:
        logger.error(f"Error in music_stream: {e}")
    return HttpResponse(ErrorMessageEnum.INTERNAL_SERVER_ERROR.value, status=500)

@login_required
@require_http_methods(['UPDATE'])
def stop_stream(request, soundboard_uuid, playlist_uuid) -> JsonResponse:
    
    SharedSoundboardService(request, soundboard_uuid).music_stop(playlist_uuid)
    
    return JsonResponse({"message": "stream stop"}, status=200)

@login_required
@require_http_methods(['POST'])
def update_direct_volume(request, playlist_uuid) -> JsonResponse:
    if request.method == 'POST':
        playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
        if not playlist:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        else :
            data = json.loads(request.body)
            volume = data.get('volume')
            if volume is not None:
                playlist.volume = volume
                playlist.save()
                return JsonResponse({"message": "volume updated"}, status=200)
        
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)

@login_required
@require_http_methods(['POST'])
def upload_multiple_music(request, playlist_uuid) -> JsonResponse:
    """Vue pour l'upload multiple de fichiers musicaux via DragAndDrop"""
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
def link_create(request, playlist_uuid):
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
    if request.method == 'DELETE':
        playlist = (PlaylistService(request)).get_playlist(playlist_uuid)
        if not playlist:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
        
        link = (LinkService(request)).get_link(link_id)
        if not link:
            return JsonResponse({"error": ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

        link.delete()
        return JsonResponse({'success': 'Suppression musique réussie'}, status=200)
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)