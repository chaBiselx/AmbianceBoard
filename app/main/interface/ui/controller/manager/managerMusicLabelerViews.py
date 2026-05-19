import os
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.architecture.persistence.models.Music import Music
from main.domain.common.service.MusicLabelerService import MusicLabelerService




@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def music_labeler_index(request) -> HttpResponse:
    """Page listant les musiques avec lecteur audio et labeling IA asynchrone."""
    musics = Music.objects.select_related('playlist').order_by('-created_at')[:100]
    music_ids = [m.id for m in musics]

    service = MusicLabelerService()
    labels_by_track = service.get_labels_grouped_by_track(music_ids)

    music_list = []
    for m in musics:
        music_list.append({
            'id': m.id,
            'name': m.get_name(),
            'file_name': m.fileName,
            'playlist_name': m.playlist.name if m.playlist else '-',
            'created_at': m.created_at,
            'duration': m.duration,
            'labels_json': json.dumps({'categories': labels_by_track[m.id]}) if m.id in labels_by_track else '',
        })

    return render(request, 'Html/Manager/music_labeler.html', {
        'title': 'Music Labeler IA',
        'musics': music_list,
    })


@login_required
@require_http_methods(['POST'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def music_labeler_analyze(request, music_id: int) -> JsonResponse:
    """Proxy : envoie le fichier audio au microservice music-labeler et retourne les labels."""
    service = MusicLabelerService()

    try:
        data = service.analyze_by_id(music_id)
        return JsonResponse(data)
    except Music.DoesNotExist:
        return JsonResponse({'error': 'Musique introuvable'}, status=404)
    except FileNotFoundError as e:
        return JsonResponse({'error': str(e)}, status=404)
    except ConnectionError:
        return JsonResponse({'error': 'Service music-labeler indisponible'}, status=503)
    except TimeoutError:
        return JsonResponse({'error': "Timeout lors de l'analyse"}, status=504)
    except RuntimeError as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def music_labeler_stream(request, music_id: int) -> HttpResponse:
    """Stream un fichier audio pour le lecteur dans le navigateur."""
    try:
        music = Music.objects.get(id=music_id)
    except Music.DoesNotExist:
        return HttpResponse(status=404)

    if not music.file or not os.path.exists(music.file.path):
        return HttpResponse(status=404)

    return music.get_reponse_content()
