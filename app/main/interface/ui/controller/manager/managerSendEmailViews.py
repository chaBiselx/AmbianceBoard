from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.manager.service.ManagerEmailService import ManagerEmailService
from main.interface.ui.forms.manager.ManagerSendEmailForm import ManagerSendEmailForm


@login_required
@require_http_methods(['GET', 'POST'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def manager_send_email(request) -> HttpResponse:
    if request.method == 'POST':
        form = ManagerSendEmailForm(request.POST)
        if form.is_valid():
            recipient_list = form.cleaned_data['recipients']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['message']
            
            queued = ManagerEmailService().dispatch(
                recipients=list(recipient_list),
                subject=subject,
                body=body,
                sender=request.user,
            )
            messages.success(request, f'{queued} email(s) mis en file d\'envoi.')
            return redirect('managerSendEmail')
    else:
        form = ManagerSendEmailForm()

    context = {
        'form': form,
    }
    return render(request, 'Html/Manager/send_email.html', context)
