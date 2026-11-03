from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_GET

from main.architecture.persistence.repository.AsyncDownloadJobRepository import AsyncDownloadJobRepository
from main.domain.brokers.message.AsyncDownloadJobMessenger import process_async_download_job
from main.domain.common.enum.AsyncDownloadJobStatusEnum import AsyncDownloadJobStatusEnum
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from main.domain.common.utils.logger import logger

@login_required
@require_GET
@permission_required("auth." + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url="login")
def manager_async_download_jobs(request):
    page_number = int(request.GET.get("page", 1))
    queryset = AsyncDownloadJobRepository().get_all_jobs()

    status = (request.GET.get('status') or '').strip()
    if status:
        if status in AsyncDownloadJobStatusEnum.__members__:
            queryset = queryset.filter(status=status)
        else:
            status = ''

    date_from = (request.GET.get("date_from") or '').strip()
    date_to = (request.GET.get("date_to") or '').strip()
    if date_to == '':
        date_to = None
    if date_from == '':
        date_from = None

    if date_from: 
        queryset = queryset.filter(created_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)

    context = extract_context_to_paginator(Paginator(queryset, 50), page_number)
    context.update({
        "title": "Téléchargements asynchrones",
        "status_list": AsyncDownloadJobStatusEnum.convert_to_dict(),
        "status": status,
        "date_to": date_to,
        "date_from": date_from
    })
    return render(request, "Html/Manager/async_download_jobs.html", context)


@login_required
@require_POST
@permission_required("auth." + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url="login")
def manager_async_download_job_retry(request, job_uuid):
    repository = AsyncDownloadJobRepository()
    job = repository.get_by_uuid(str(job_uuid))
    if job is None:
        raise Http404("Téléchargement introuvable.")

    if job.status != AsyncDownloadJobStatusEnum.PENDING.name:
        messages.error(request, "Seuls les téléchargements en attente peuvent être relancés.")
        return redirect("managerAsyncDownloadJobs")

    result = process_async_download_job.apply_async(
        args=[str(job.uuid)],
        queue="default",
        priority=1,
    )
    repository.set_task_id(job, result.id)
    logger.info(
        "AsyncDownloadJob relancé par Manager: job_uuid=%s user_id=%s celery_task_id=%s",
        job.uuid,
        request.user.id,
        result.id,
    )
    messages.success(request, "Le téléchargement a été relancé.")
    return redirect("managerAsyncDownloadJobs")
