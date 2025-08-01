from functools import wraps
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.urls import reverse
from main.utils.ServerNotificationBuilder import ServerNotificationBuilder






# Configurer le logger
from main.utils.logger import logger

def detect_not_confirmed_account():
    """
    Décorateur qui affiche un message flash si l'addresse email n'est pas confirmé
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.isConfirmed == False:
                    url = reverse("resend_email_confirmation")
                    ServerNotificationBuilder(request).set_message(f'Votre addresse email n\'est pas confirmé, merci de regarder dans vos email <br/> <button class="btn btn-secondary" id="resend_email_confirmation_account" data-url="{url}" >Renvoyer un email de confirmation</button>').set_statut("info").send()
                
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator