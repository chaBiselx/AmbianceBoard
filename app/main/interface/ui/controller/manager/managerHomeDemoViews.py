from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from main.domain.common.utils.logger import logger
from main.architecture.persistence.repository.HomeDemoItemRepository import HomeDemoItemRepository
from main.architecture.persistence.repository.TagRepository import TagRepository
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.interface.ui.forms.manager.HomeDemoItemForm import HomeDemoItemForm


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def listing_home_demo_items(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    queryset = HomeDemoItemRepository().get_all_items()
    paginator = Paginator(queryset, 50)
    context = extract_context_to_paginator(paginator, page_number)
    context.update({'title': "Liste des éléments Home Demo"})
    return render(request, 'Html/Manager/home_demo_listing.html', context)


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def select_home_demo_soundboard(request) -> HttpResponse:
    page_number = int(request.GET.get('page', 1))
    selected_tag = request.GET.get('tag', None)

    queryset = HomeDemoItemRepository().get_selectable_public_queryset(selected_tag)
    paginator = Paginator(queryset, 100)
    context = extract_context_to_paginator(paginator, page_number)
    context.update({
        'title': 'Sélectionner un soundboard public',
        'listTags': TagRepository().get_tag_with_count(),
        'selected_tag': selected_tag,
        'soundboards': context['page_objects'],
        'used_soundboard_ids': HomeDemoItemRepository().get_used_soundboard_ids(),
    })
    return render(request, 'Html/Manager/home_demo_soundboard_select.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def manage_home_demo_item(request, uuid=None, soundboard_uuid=None) -> HttpResponse:
    item = None
    selected_soundboard = None
    is_update = uuid is not None

    if is_update:
        item = HomeDemoItemRepository().get_item_by_uuid(uuid)
        if item is None:
            messages.error(request, "Élément introuvable.")
            return redirect('managerHomeDemoItems')
    else:
        if soundboard_uuid is None:
            messages.error(request, "Veuillez d'abord choisir un soundboard public.")
            return redirect('managerHomeDemoSelectSoundboard')
        selected_soundboard = SoundBoardRepository().get(soundboard_uuid)
        if selected_soundboard is None or not selected_soundboard.is_public:
            messages.error(request, "Soundboard public introuvable ou non autorisé.")
            return redirect('managerHomeDemoSelectSoundboard')
        if selected_soundboard.id in HomeDemoItemRepository().get_used_soundboard_ids():
            messages.error(request, "Ce soundboard est déjà utilisé dans la démo.")
            return redirect('managerHomeDemoSelectSoundboard')

    if request.method == 'POST':
        form = HomeDemoItemForm(request.POST, instance=item, selected_soundboard=selected_soundboard)
        if form.is_valid():
            item = form.save()
            action_msg = 'modifié' if is_update else 'créé'
            messages.success(request, f"Élément {action_msg} avec succès.")
            logger.info(f"Home demo item {action_msg}: {item.uuid} par {request.user.username}")
            return redirect('managerHomeDemoItems')
    else:
        form = HomeDemoItemForm(instance=item, selected_soundboard=selected_soundboard)

    context = {
        'title': "Modifier un élément Home Demo" if is_update else "Créer un élément Home Demo",
        'form': form,
        'item': item,
        'selected_soundboard': selected_soundboard,
        'action': 'update' if is_update else 'create',
    }
    return render(request, 'Html/Manager/home_demo_form.html', context)
