import uuid
import logging
import time

class LogRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request')
        self.logger_home = logging.getLogger('home')

    def __call__(self, request):
        start_time = time.time()
        
        if request.user.is_authenticated: # If the user is authenticated
            unique_id = f"USER_{request.user.uuid}"
            response = self.get_response(request)
        else: # If the user is not authenticated
            unique_id = request.COOKIES.get('unique_id')
            if not unique_id: # If the cookie is not set
                unique_id = f"COOKIE_{uuid.uuid4()}"
                response = self.get_response(request)
                response.set_cookie('unique_id', unique_id, max_age=3600)  # Set cookie for 1 hour
            else:
                response = self.get_response(request)
            
        duration = round(time.time() - start_time, 6)

        # Nettoyer les champs sensibles du POST
        filtered_post = {
            k: ("***" if "password" in k.lower() or "secret" in k.lower() or "token" in k.lower() else v)
            for k, v in request.POST.items()
        }

        # Logger les informations sans les champs sensibles
        self.logger.info(
            '',
            extra={
                'method': request.method,
                'request': request.get_full_path(),
                'post': filtered_post,
                'status': response.status_code,
                'duration': duration,
                'unique_id': unique_id
            }
        )

        self.logger_home.info(
            f"REQUEST : {request.method:<8} {request.get_full_path()} {filtered_post} {response.status_code} {duration}sec id:{unique_id}"
        )

        return response

