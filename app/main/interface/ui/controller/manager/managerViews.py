from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from main.domain.manager.service.UserStatsService import UserStatsService
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.manager.service.UserActivityStatsService import UserActivityStatsService
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def manager_dashboard(request) -> HttpResponse:
    periode_chart = request.GET.get('periode-chart', '91')
    
    select_periods = {
        "7" : "1 semaine",
        "14" : "2 semaines",
        "31" : "1 mois",
        "61" : "2 mois",
        "91" : "3 mois",
        "183" : "6 mois",
        "365" : "1 an",
    }
    if periode_chart not in select_periods:
        periode_chart = "91"
                                
    
    return render(request, 'Html/Manager/dashboard.html', {'title': 'Tableau de bord Manager', 'periode_chart': periode_chart, 'selectPeriods':select_periods})

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def user_account_dashboard(request) -> JsonResponse:
    """
    Récupère les données pour chart.js :
    - Nombre d'utilisateurs créés par jour (date_joined)
    - Nombre de connexions par jour (last_login)
    
    Returns:
        JsonResponse: Données formatées pour chart.js avec les labels (dates) 
                     et les datasets (créations et connexions)
    """
    try:
        # Définir la période (30 derniers jours par défaut)
        days = int(request.GET.get('period', 30 * 6))
        end_date = timezone.now().date() + timedelta(days=1)
        start_date = end_date - timedelta(days=days-1)

        response_data = UserStatsService.get_user_activity_data(start_date, end_date)
        json = {
            'title' : f"Évolution des utilisateurs - {days} jours",
            'x_label': 'Date',
            'y_label': 'Utilisateurs',
            'data':response_data
        }
        return JsonResponse(json)
        
    except Exception as e:
        return JsonResponse({
            'error': ErrorMessageEnum.DATA_RECUPERATION,
            'message': str(e)
        }, status=500)
    

@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def user_activity_dashboard(request) -> JsonResponse:
    try:
        days = int(request.GET.get('period', 30 * 6))
        end_date = timezone.now().date() + timedelta(days=1)
        start_date = end_date - timedelta(days=days-1)

        service = UserActivityStatsService()
        response_data = service.get_user_nb_activity_data(start_date, end_date)

        json = {
            'title' : f"Évolution des consultations - {days} jours",
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
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def error_activity_dashboard(request) -> JsonResponse:
    try:
        days = int(request.GET.get('period', 30 * 6))
        end_date = timezone.now().date() + timedelta(days=1)
        start_date = end_date - timedelta(days=days-1)

        service = UserActivityStatsService()
        response_data = service.get_error_activity_data(start_date, end_date)
        
        json = {
            'title' : f"Évolution des erreurs - {days} jours",
            'x_label': 'Date',
            'y_label': 'Erreurs',
            'data':response_data
        }
        return JsonResponse(json)

    except Exception as e:
        return JsonResponse({
            'error': ErrorMessageEnum.DATA_RECUPERATION,
            'message': str(e)
        }, status=500)
