import json
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.forms import formset_factory
from main.utils.settings import Settings
from main.domain.common.service.PlaylistService import PlaylistService
from main.service.SoundBoardService import SoundBoardService
from main.forms.PlaylistColorUserForm import PlaylistColorUserForm
from main.models.PlaylistColorUser import PlaylistColorUser
from main.models.UserPreference import UserPreference
from main.domain.common.service.DefaultColorPlaylistService import DefaultColorPlaylistService
from main.domain.common.enum.ThemeEnum import ThemeEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.common.exceptions.PostDataException import PostDataException
from main.utils.UserTierManager import UserTierManager
from main.utils.logger import logger

@login_required
@require_http_methods(['GET'])
def settings_index(request):
    user_tiers = UserTierManager.get_tier_display_name(request.user)
    limit = UserTierManager.get_user_limits(request.user)
    nb_playlist = len(PlaylistService(request).get_all_playlist())
    nb_soundboard = len(SoundBoardService(request).get_all_soundboard())
    app_setting = {
        'target_bitrate': Settings.get('AUDIO_BITRATE_REDUCER_TARGET_BITRATE')
    }
    return render(request, 'Html/Account/Settings/index.html', {'limit': limit, 'user_tiers': user_tiers, 'nb_playlist': nb_playlist, 'nb_soundboard': nb_soundboard, 'app_setting': app_setting})

@login_required
@require_http_methods(['POST', 'GET'])
def settings_update_default_style(request):
    playlist_color_user_form_set = formset_factory(PlaylistColorUserForm, extra=0)
    
    default_color_playlist = DefaultColorPlaylistService(request.user)
    initial_data = default_color_playlist.get_list_default_color()

    if request.method == "POST":
        try:
            formset = playlist_color_user_form_set(request.POST)
            if formset.is_valid():
                for form in formset:
                    if form.cleaned_data:
                        type_playlist = form.cleaned_data["typePlaylist"]
                        color = form.cleaned_data["color"]
                        color_text = form.cleaned_data["colorText"]
                        
                        # Mise à jour ou création de l'entrée
                        pcu, created = PlaylistColorUser.objects.get_or_create(user=request.user, typePlaylist=type_playlist)
                        pcu.color = color
                        pcu.colorText = color_text
                        if(created):
                            pcu.user = request.user
                            logger.debug(f"pcu.user: {pcu}")
                        pcu.save()
                        
                
                return redirect('defaultPlaylistType')
        except Exception as e:
            logger.error(f"settings_update_default_style error : {e}")
            return render(request, 'Html/Account/Settings/update_default_style_playlist.html', {'formset': formset})
    else:
        formset = playlist_color_user_form_set(initial=initial_data)
    
    return render(request, 'Html/Account/Settings/update_default_style_playlist.html', {'formset': formset})

@login_required
@require_http_methods(['UPDATE'])
def update_theme(request):
    if request.method == 'UPDATE':
        try:
            data = json.loads(request.body)  # Décode le JSON
            if 'theme' not in data:
                raise PostDataException('Theme not found in request data.')
            
            new_theme = data['theme']
            enum_theme = ThemeEnum(new_theme)
            user_preference, _ = UserPreference.objects.get_or_create(user=request.user)
            user_preference.theme = enum_theme.value
            user_preference.save()
            return JsonResponse({'message': 'Theme updated successfully.'}, status=200)
        except Exception as e:
            logger.error(f"update theme error : {e}")
            return JsonResponse({'error': 'Failed to update theme.'}, status=500)
    return JsonResponse({'error': ErrorMessageEnum.INVALID_REQUEST_METHOD.value}, status=400)

@login_required
@require_http_methods(['GET'])
def update_dimensions(request):
    return render(request, 'Html/Account/Settings/update_dimensions.html')

@login_required
@require_http_methods(['UPDATE'])
def update_playlist_dim(request):
    if request.method == 'UPDATE':
        try:
            data = json.loads(request.body)  # Décode le JSON
            if 'dim' not in data:
                raise PostDataException('dim not found in request data.')
            dim = data['dim']
            user_preference, _ = UserPreference.objects.get_or_create(user=request.user)
            user_preference.playlistDim = dim
            user_preference.save()
            return JsonResponse({'message': 'Dimensions updated successfully.'}, status=200)
        except Exception as e:
            logger.error(f"update dimensions playlist error : {e}")
            return JsonResponse({'error': 'Failed to update dimensions.'}, status=500)
    return JsonResponse({'error': ErrorMessageEnum.INVALID_REQUEST_METHOD.value}, status=400)

@login_required
@require_http_methods(['UPDATE'])
def update_soundboard_dim(request):
    if request.method == 'UPDATE':
        try:
            data = json.loads(request.body)  # Décode le JSON
            if 'dim' not in data:
                raise PostDataException('dim not found in request data.')
            dim = data['dim']
            user_preference, _ = UserPreference.objects.get_or_create(user=request.user)
            user_preference.soundboardDim = dim
            user_preference.save()
            return JsonResponse({'message': 'Dimensions updated successfully.'}, status=200)
        except Exception as e:
            logger.error(f"update dimensions soundboard error : {e}")
            return JsonResponse({'error': 'Failed to update dimensions.'}, status=500)
    return JsonResponse({'error': ErrorMessageEnum.INVALID_REQUEST_METHOD.value}, status=400)

@login_required
@require_http_methods(['GET', 'DELETE'])
def delete_account(request):
    if request.method == 'GET':
        return render(request, 'Html/Account/Settings/delete_account.html')
    if request.method == 'DELETE':
        try:
            user = request.user
            user.delete()
            logout(request)
            logger.info(f"User {user.username} deleted successfully.")
            return JsonResponse({'message': 'Account deleted successfully.'}, status=200)
        except Exception as e:
            logger.error(f"delete account error : {e}")
            return JsonResponse({'error': 'Failed to delete account.'}, status=500)
    return JsonResponse({'error': ErrorMessageEnum.INVALID_REQUEST_METHOD.value}, status=400)
