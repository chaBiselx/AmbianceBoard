from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from main.architecture.persistence.repository.HomeDemoItemRepository import HomeDemoItemRepository
from main.architecture.persistence.repository.TagRepository import TagRepository
from main.domain.manager.service.ManageHomeDemoItemService import ManageHomeDemoItemService


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
    service = ManageHomeDemoItemService()
    
    # Récupère et valide les données initiales
    item, selected_soundboard, is_update, error_message = service.get_initial_data(uuid, soundboard_uuid)
    if error_message:
        messages.error(request, error_message)
        return redirect('managerHomeDemoItems' if is_update else 'managerHomeDemoSelectSoundboard')

    # Traite la soumission du formulaire (POST)
    form = None
    if request.method == 'POST':
        is_valid, saved_item, form = service.process_form_submission(request.POST, item, selected_soundboard)
        if is_valid:
            messages.success(request, service.get_success_message(is_update))
            service.log_item_action(saved_item, is_update, request.user.username)
            return redirect('managerHomeDemoItems')
    
    # Crée le formulaire pour GET (si pas déjà créé lors du POST)
    if form is None:
        form = service.get_form(item, selected_soundboard)
    
    context = service.get_context(form, item, selected_soundboard, is_update)
    
    return render(request, 'Html/Manager/home_demo_form.html', context)
