import logging
import os
import mimetypes
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import FileResponse,Http404
from home.enum.PermissionEnum import PermissionEnum
from parameters import settings



    

@login_required
@permission_required('auth.' + PermissionEnum.MODERATEUR_ACCESS_DASHBOARD.name)
def static_protected_moderator_js(request, folder:str, filename: str ) -> FileResponse:
    
    protected_dir = os.path.join(settings.BASE_DIR, f'staticProtected/moderator/{folder}')
    
    file_path = os.path.join(protected_dir, filename)
    print(file_path)
    if not os.path.isfile(file_path):
        return Http404("Fichier non trouvé.")
    
    content_type, _ = mimetypes.guess_type(file_path)
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
    
@login_required
@permission_required('auth.' + PermissionEnum.MANAGER_ACCESS_DASHBOARD.name)
def static_protected_manager_js(request, folder:str, filename: str ) -> FileResponse:
    
    protected_dir = os.path.join(settings.BASE_DIR, f'staticProtected/manager/{folder}')
    
    file_path = os.path.join(protected_dir, filename)
    print(file_path)
    if not os.path.isfile(file_path):
        return Http404("Fichier non trouvé.")
    
    content_type, _ = mimetypes.guess_type(file_path)
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
    

