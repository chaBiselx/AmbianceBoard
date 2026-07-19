from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from main.architecture.persistence.repository.AsyncDownloadJobRepository import AsyncDownloadJobRepository
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator


@login_required
@require_http_methods(["GET"])
def recent_async_download_jobs(request):
    page_number = int(request.GET.get("page", 1))
    queryset = AsyncDownloadJobRepository().get_recent_jobs_for_user(request.user)
    paginator = Paginator(queryset, 50)
    context = extract_context_to_paginator(paginator, page_number)
    context.update(
        {
            "title": "Téléchargements récents",
        }
    )
    return render(request, "Html/Account/async_download_jobs_recent.html", context)
