from django.views.decorators.http import require_http_methods
from main.domain.common.utils.logger import LoggerFactory
from django.http import JsonResponse, HttpRequest
import json


@require_http_methods(['POST'])
def trace_front(request: HttpRequest) -> JsonResponse:
    logger = LoggerFactory.get_default_logger('front')
    
    try:
        # Parse JSON body instead of POST data
        data = json.loads(request.body)
        level = data.get('level', 'unknown')
        messages = data.get('messages', [])
        timestamp = data.get('timestamp', '')
        
        # Convert messages array to string for logging
        messages_str = ' | '.join(str(msg) for msg in messages) if messages else 'No message'
        
        # Log with level and formatted messages
        log_message = f"[{timestamp}] {level.upper()}: {messages_str}"
        logger.info(log_message)
        
    except json.JSONDecodeError:
        # Log raw request body if JSON parsing fails
        raw_body = request.body.decode('utf-8', errors='replace')
        logger.error(f"Invalid JSON in trace request - Raw body: {raw_body}")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        # Log raw request body and error details
        raw_body = request.body.decode('utf-8', errors='replace')
        logger.error(f"Error processing trace request: {str(e)} - Raw body: {raw_body}")
        return JsonResponse({"error": "Internal error"}, status=500)
    
    return JsonResponse({"message": "ok"}, status=200)
    