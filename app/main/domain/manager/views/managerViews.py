from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from main.domain.manager.service.UserStatsService import UserStatsService
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.manager.service.UserActivityStatsService import UserActivityStatsService


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def manager_dashboard(request) -> HttpResponse:
    return render(request, 'Html/Manager/dashboard.html')

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
        print(response_data)
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Erreur lors de la récupération des données',
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

        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Erreur lors de la récupération des données',
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
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'error': 'Erreur lors de la récupération des données',
            'message': str(e)
        }, status=500)
