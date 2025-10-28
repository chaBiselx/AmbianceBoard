from functools import wraps
from typing import Callable
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.common.enum.ErrorMessageEnum import ErrorMessageEnum
from main.domain.common.utils.logger import logger


def cron_view(view_name: str) -> Callable:
    """
    Decorator for cron views that handles:
    - Authentication and permissions
    - HTTP method restriction (GET only)
    - Error handling with JSON response
    - Logging (start/end)
    
    Args:
        view_name: Name of the cron job for logging purposes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @login_required
        @require_http_methods(['GET'])
        @permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
        def wrapper(request, *args, **kwargs):
            try:
                logger.warning(f"Starting {view_name} View")
                func(request, *args, **kwargs)
                logger.warning(f"Ending {view_name} View")
                return JsonResponse({"message": "OK"}, status=200)
            except Exception as e:
                logger.error(f"Error in {view_name} View: {str(e)}")
                return JsonResponse(
                    {"error": ErrorMessageEnum.INTERNAL_SERVER_ERROR.value, "message": str(e)}, 
                    status=500
                )
        return wrapper
    return decorator
