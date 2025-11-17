from django.utils import timezone
from datetime import datetime, timedelta
from django.template.response import TemplateResponse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from main.domain.common.enum.HtmlDefaultPageEnum import HtmlDefaultPageEnum
from main.domain.public.decorator.accessPublicStats import can_show_statistics
from main.domain.common.utils.ExtractPaginator import extract_context_to_paginator
from django.core.paginator import Paginator
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.domain.common.enum.ChartPeriodEnum import ChartPeriodEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.public.service.UserPublicActivityStatsService import UserPublicActivityStatsService




@login_required
@can_show_statistics
@require_http_methods(['GET'])
def list_user_public_soundboard(request):
    page_number = int(request.GET.get('page', 1))
    
    # Filtrage par tag si spécifié
    queryset = SoundBoardRepository().get_list_public_queryset(request.user)
    paginator = Paginator(queryset, 25)  
    context = extract_context_to_paginator(paginator, page_number)
    return TemplateResponse(request, 'Html/Public/list_user_public_soundboard.html', context)


@login_required
@can_show_statistics
@require_http_methods(['GET'])
def stats_user_public_soundboard(request, soundboard_uuid):
    periode_chart = request.GET.get('periode-chart', "0")
    
    select_periods = ChartPeriodEnum.get_days_mapping()
    if not ChartPeriodEnum.is_valid_period(periode_chart):
        periode_chart = ChartPeriodEnum.get_default_period()
        
    soundboard = SoundBoardRepository().get_by_uuid_and_user(soundboard_uuid, request.user)
    if(not soundboard):
        return TemplateResponse(request, HtmlDefaultPageEnum.NOT_FOUND.value, status=404)
    return TemplateResponse(request, 'Html/Public/stats_user_public_soundboard.html', {'title': f'Statistiques de la soundboard {soundboard.name}', 'periode_chart': periode_chart, 'selectPeriods':select_periods, 'soundboard':soundboard})


@login_required
@can_show_statistics
@require_http_methods(['GET'])
def stats_frequentation(request, soundboard_uuid) -> JsonResponse:
    try:
        days = int(request.GET.get('period', 30 * 6))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        soundboard = SoundBoardRepository().get_by_uuid_and_user(soundboard_uuid, request.user)
        if(not soundboard):
            raise Exception("Soundboard non trouvée")

        service = UserPublicActivityStatsService()
        response_data = service.get_frequentation(soundboard, start_date, end_date)

        json = {
            'title' : f"Évolution des fréquentations - {days} jours",
            'x_label': 'Date',
            'y_label': 'Consultations',
            'data':response_data
        }
        return JsonResponse(json)
        
    except Exception as e:
        return JsonResponse({
            'error': ErrorMessageEnum.DATA_RECUPERATION,
            'message': str(e)
        }, status=500)
       
       
@login_required
@can_show_statistics
@require_http_methods(['GET']) 
def stats_moyenne_duration_session(request, soundboard_uuid) -> JsonResponse:
    try:
        days = int(request.GET.get('period', 30 * 6))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        soundboard = SoundBoardRepository().get_by_uuid_and_user(soundboard_uuid, request.user)
        if(not soundboard):
            raise Exception("Soundboard non trouvée")

        service = UserPublicActivityStatsService()
        response_data = service.get_moyenne_duration_session(soundboard, start_date, end_date)

        json = {
            'title' : f"Durée moyenne des sessions - {days} jours",
            'x_label': 'Date',
            'y_label': 'Durée Moyenne des Sessions (min)',
            'data':response_data
        }
        return JsonResponse(json)
        
    except Exception as e:
        return JsonResponse({
            'error': ErrorMessageEnum.DATA_RECUPERATION,
            'message': str(e)
        }, status=500)
    