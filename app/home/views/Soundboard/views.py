import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ...models.SoundBoard import SoundBoard
from ...service.SoundBoardService import SoundBoardService
from ...forms.SoundBoardForm import SoundBoardForm
from ...filters.SoundBoardFilter import SoundBoardFilter


@login_required
def soundboard_list(request):
    logger = logging.getLogger(__name__)
    logger.info(request.user)
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
    return render(request, 'Soundboard/soundboard_form.html', {'form': form })

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
    return render(request, 'Soundboard/soundboard_form.html', {'form': form})

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
