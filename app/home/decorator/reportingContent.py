import functools
from django.template.response import TemplateResponse
from django.urls import reverse

def add_reporting_btn():  # Paramètres ajoutés ici
# def add_reporting_btn(typeElement:str, uuid:str):  # Paramètres ajoutés ici
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            if isinstance(response, TemplateResponse):
                if response.context_data is None:
                    response.context_data = {}

                # Exemple d'utilisation des paramètres
                response.context_data.update({
                    'reportingContentUrl': reverse("publicReportingContent"),
                })

            return response

        return _wrapped_view
    return decorator