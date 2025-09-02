import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from main.service.MusicService import MusicService
from main.service.RandomizeTrackService import RandomizeTrackService
from main.domain.common.service.PlaylistService import PlaylistService
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.private.form.PlaylistForm import PlaylistForm
from main.domain.common.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from main.domain.common.enum.LinkMusicAllowedEnum import LinkMusicAllowedEnum
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum
from main.domain.common.enum.ConfigTypeDataEnum import ConfigTypeDataEnum
from main.domain.private.formatter.TypePlaylistFormater import TypePlaylistFormater
from main.service.SoundBoardService import SoundBoardService

from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.ActivityContextHelper import ActivityContextHelper
from main.domain.common.repository.SoundBoardRepository import SoundBoardRepository
from main.domain.common.repository.PlaylistRepository import PlaylistRepository



from main.domain.common.utils.logger import logger

@login_required
@require_http_methods(['GET'])
def playlist_read_all(request):
    playlists = (PlaylistService(request)).get_all_playlist()
    return render(request, 'Html/Playlist/playlist_read_all.html', {'playlists': playlists})


@login_required
@require_http_methods(['GET', 'POST'])
def playlist_create(request):
    if request.method == 'POST':
        playlist = (PlaylistService(request)).save_form()
        ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.PLAYLIST_CREATE, user=request.user, content_object=playlist)
        return redirect('playlistUpdate', playlist_uuid=playlist.uuid)
    else:
        form = PlaylistForm()
    list_default_color = DefaultColorPlaylistService(request.user).get_list_default_color()
    link_music_allowed_values = LinkMusicAllowedEnum.values()
    return render(
        request,
        'Html/Playlist/playlist_create.html', # NOSONAR
        {'form': form , 'method' : 'create', 'listMusic': None, 'list_default_color': list_default_color,'LinkMusicAllowedEnum': link_music_allowed_values}
    )

@login_required
@require_http_methods(['GET', 'POST'])
def playlist_create_with_soundboard(request, soundboard_uuid):
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if(soundboard) : 
        if request.method == 'POST':
            playlist = (PlaylistService(request)).save_form()
            if(playlist):
                soundboard.playlists.add(playlist)
                ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.PLAYLIST_CREATE, user=request.user, content_object=playlist)
            return redirect('soundboardsRead', soundboard_uuid=soundboard.uuid)
        else:
            form = PlaylistForm()
        list_default_color = DefaultColorPlaylistService(request.user).get_list_default_color()
        link_music_allowed_values = LinkMusicAllowedEnum.values()
        return render(
            request, 
            'Html/Playlist/playlist_create.html', # NOSONAR
            {'form': form, 'method': 'create', 'listMusic': None, 'list_default_color': list_default_color, 'LinkMusicAllowedEnum': link_music_allowed_values}
        )
    return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404) 

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
    link_music_allowed_values = LinkMusicAllowedEnum.values()
    return render(
        request, 
        'Html/Playlist/playlist_create.html', # NOSONAR
        {'form': form, 'method' : 'update', 'listTrack' : list_track, 'list_default_color':list_default_color, 'LinkMusicAllowedEnum': link_music_allowed_values}
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
    """Retourne les couleurs de playlists déja utilisées"""
    default_playlists = DefaultColorPlaylistService(request.user).get_list_default_color_ajax()

    unique_playlists = PlaylistRepository().get_distinct_styles()
    for playlist in unique_playlists:
        playlist['typePlaylist'] = PlaylistTypeEnum[playlist['typePlaylist']].value
    return JsonResponse({"unique_playlists": list(unique_playlists), "default_playlists": list(default_playlists)}, status=200)


@login_required
@require_http_methods(['GET'])
def playlist_create_track_stream(request, playlist_uuid, music_id) -> HttpResponse | StreamingHttpResponse:
    """Stream d'une track spécifique d'une playlist"""
    track = (MusicService(request)).get_specific_music(playlist_uuid, music_id)
    if not track:
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
            ActivityContextHelper.set_action(request, activity_type=UserActivityTypeEnum.PLAYLIST_DELETE, user=request.user, content_object=playlist)
            PlaylistRepository().delete(playlist)

            return JsonResponse({'success': 'Suppression playlist réussie'}, status=200)
    return JsonResponse({"error": ErrorMessageEnum.METHOD_NOT_SUPPORTED.value}, status=405)
   