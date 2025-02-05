import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from home.utils.ExtractPaginator import extract_context_to_paginator
from home.models.SoundBoard import SoundBoard
from home.service.SoundBoardService import SoundBoardService
from home.service.MusicService import MusicService
from home.decorator.detectBan import detect_ban


def public_index(request):
    return redirect('publicListingSoundboard')

def public_listing_soundboard(request):
    page_number = int(request.GET.get('page', 1))
    
    queryset = SoundBoard.objects.filter(is_public=True)
    paginator = Paginator(queryset, 100)  
    context = extract_context_to_paginator(paginator, page_number)
    
    return render(request, 'Html/Public/listing_soundboard.html', context)

@detect_ban
def public_soundboard_read_playlist(request, soundboard_id):
    soundboard = (SoundBoardService(request)).get_public_soundboard(soundboard_id)
    if not soundboard:
        return render(request, '404.html', status=404)
    else:   
        return render(request, 'Html/Public/soundboard_read.html', {'soundboard': soundboard})
    
@detect_ban
def public_music_stream(request, soundboard_id, playlist_id) -> HttpResponse:
 
    music = (MusicService(request)).get_public_random_music(soundboard_id, playlist_id)
    if not music :
        return HttpResponse("Musique introuvable.", status=404)
    
    response = HttpResponse(music.file, content_type='audio/*')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(music.fileName)
    return response