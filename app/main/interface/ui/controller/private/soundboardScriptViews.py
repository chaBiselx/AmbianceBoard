import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.common.enum.ScriptActionEnum import ScriptActionEnum
from main.domain.common.enum.ScriptTriggerEnum import ScriptTriggerEnum
from main.domain.common.exceptions.SoundboardScriptException import SoundboardScriptException
from main.domain.common.service.SoundBoardService import SoundBoardService
from main.domain.common.service.script.ScriptActionSpecRegistry import ScriptActionSpecRegistry
from main.domain.common.service.script.SoundboardScriptService import SoundboardScriptService
from main.domain.common.service.script.ScriptResolverService import ScriptResolverService

from main.domain.common.utils.logger import logger


@login_required
@require_http_methods(['GET'])
def soundboard_scripts(request, soundboard_uuid):
    """Page d'édition des scripts d'un soundboard"""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)

    return render(request, 'Html/Soundboard/soundboard_scripts.html', {
        'soundboard': soundboard,
        'scripts': SoundboardScriptService(soundboard).get_all(),
        'title': _('template.scripts.page.title'),
    })


@login_required
@require_http_methods(['POST'])
def soundboard_script_create(request, soundboard_uuid):
    """Création d'un script"""
    soundboard = (SoundBoardService(request)).get_soundboard(soundboard_uuid)
    if not soundboard:
        return JsonResponse({'error': _('template.scripts.error.soundboard_not_found')}, status=404)

    name = (request.POST.get('name') or '').strip()
    if not name:
        return JsonResponse({'error': _('template.scripts.error.name_required')}, status=400)

    script = SoundboardScriptService(soundboard).create(name=name)
    return JsonResponse({'success': True, 'script_uuid': str(script.uuid)}, status=201)


@login_required
@require_http_methods(['POST'])
def soundboard_script_update(request, soundboard_uuid, script_uuid):
    """Mise à jour des propriétés d'un script"""
    try:
        resolver = ScriptResolverService(request)
        soundboard = resolver.get_soundboard(soundboard_uuid)
        script = resolver.get_script(script_uuid)
        service = resolver.get_script_service()

        fields = {}
        if 'name' in request.POST:
            name = (request.POST.get('name') or '').strip()
            if not name:
                return JsonResponse({'error': _('template.scripts.error.name_required')}, status=400)
            fields['name'] = name
        if 'enabled' in request.POST:
            fields['enabled'] = request.POST['enabled'] == 'true'

        service.update(script, **fields)
        return JsonResponse({'success': True}, status=200)
    except ValueError as ve:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
    except Exception as e:
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)


@login_required
@require_http_methods(['DELETE'])
def soundboard_script_delete(request, soundboard_uuid, script_uuid):
    """Suppression d'un script et de ses étapes"""
    try:
        resolver = ScriptResolverService(request)
        soundboard = resolver.get_soundboard(soundboard_uuid)
        script = resolver.get_script(script_uuid)
        service = resolver.get_script_service()
        if script is None:
            return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)

        service.delete(script)
        return JsonResponse({'success': True}, status=200)
    except ValueError as ve:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
    except Exception as e:
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)


@login_required
@require_http_methods(['GET'])
def soundboard_script_steps(request, soundboard_uuid, script_uuid):
    """Fragment HTML listant et éditant les étapes d'un script"""
    try:
        resolver = ScriptResolverService(request)
        soundboard = resolver.get_soundboard(soundboard_uuid)
        script = resolver.get_script(script_uuid)
        service = resolver.get_script_service()

        steps = service.step_repository.get_all(script)
        return render(request, 'Html/partial/soundboard/script_steps.html', {
            'soundboard': soundboard,
            'script': script,
            'steps': steps,
            'playlists': soundboard.playlists.all().order_by('name'),
            'action_types': [(action.name, action.value) for action in ScriptActionEnum.editable_actions()],
            'trigger_types': ScriptTriggerEnum.convert_to_choices(),
            'params_by_action': json.dumps({
                action.name: ScriptActionSpecRegistry.required_keys(action.name) for action in ScriptActionEnum.editable_actions()
            }),
        })
        
    except ValueError as ve:
        return render(request, HtmlDefaultPageEnum.ERROR_404.value, status=404)
    except Exception as e:
        return render(request, HtmlDefaultPageEnum.ERROR_500.value, status=500)


@login_required
@require_http_methods(['POST'])
def soundboard_script_step_save(request, soundboard_uuid, script_uuid):
    """Création ou mise à jour d'une étape de script"""
    
    try:
        resolver = ScriptResolverService(request)
        soundboard = resolver.get_soundboard(soundboard_uuid)
        script = resolver.get_script(script_uuid)
        service = resolver.get_script_service()
        if script is None:
            return JsonResponse({'error': _('template.scripts.error.script_not_found')}, status=404)
    except ValueError as ve:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
    except Exception as e:
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)

    action_type = request.POST.get('action_type', '')
    trigger_type = request.POST.get('trigger_type', '')

    try:
        params = {
            key: request.POST.get(key)
            for key in ScriptActionSpecRegistry.required_keys(action_type)
        }
        payload = {
            'action_type': action_type,
            'trigger_type': trigger_type,
            'params': params,
            'trigger_offset_ms': int(request.POST.get('trigger_offset_ms') or 0),
            'trigger_source_step_uuid': request.POST.get('trigger_source_step_uuid') or None,
        }

        step_uuid = request.POST.get('step_uuid')
        if step_uuid:
            step = service.step_repository.get(script, step_uuid)
            if step is None:
                return JsonResponse({'error': _('template.scripts.error.step_not_found')}, status=404)
            service.update_step(script, step, **payload)
        else:
            service.add_step(script, **payload)
    except SoundboardScriptException as error:
        return JsonResponse({'error': str(error)}, status=400)
    except (TypeError, ValueError) as error:
        logger.error(f"soundboard_script_step_save : {error}")
        return JsonResponse({'error': _('template.scripts.error.invalid_step')}, status=400)

    return JsonResponse({'success': True}, status=200)


@login_required
@require_http_methods(['DELETE'])
def soundboard_script_step_delete(request, soundboard_uuid, script_uuid, step_uuid):
    """Suppression d'une étape de script"""
    try:
        resolver = ScriptResolverService(request)
        soundboard = resolver.get_soundboard(soundboard_uuid)
        script = resolver.get_script(script_uuid)
        service = resolver.get_script_service()
        if script is None:
            return JsonResponse({'error': _('template.scripts.error.script_not_found')}, status=404)
    except ValueError as ve:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
    except Exception as e:
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)

    step = service.step_repository.get(script, step_uuid)
    if step is None:
        return JsonResponse({'error': _('template.scripts.error.step_not_found')}, status=404)

    service.delete_step(step)
    return JsonResponse({'success': True}, status=200)


@login_required
@require_http_methods(['POST'])
def soundboard_script_steps_reorder(request, soundboard_uuid, script_uuid):
    """Réordonnancement des étapes d'un script"""
    try:
        resolver = ScriptResolverService(request)
        soundboard = resolver.get_soundboard(soundboard_uuid)
        script = resolver.get_script(script_uuid)
        service = resolver.get_script_service()
        if script is None:
            return JsonResponse({'error': _('template.scripts.error.script_not_found')}, status=404)
    except ValueError as ve:
        return JsonResponse({'error': ErrorMessageEnum.ELEMENT_NOT_FOUND.value}, status=404)
    except Exception as e:
        return JsonResponse({'error': ErrorMessageEnum.INTERNAL_SERVER_ERROR.value}, status=500)

    try:
        ordered_uuids = json.loads(request.body.decode('utf-8')).get('steps', [])
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error': _('template.scripts.error.invalid_step')}, status=400)

    service.reorder_steps(script, ordered_uuids)
    return JsonResponse({'success': True}, status=200)



