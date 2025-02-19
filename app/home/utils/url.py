from django.conf import settings

def get_full_url(path):
    scheme = settings.APP_SCHEME
    host = settings.APP_HOST
    port = ''
    if(settings.APP_PORT):
        port = ':' + str(settings.APP_PORT)
    return f"{scheme}://{host}{port}{path}"