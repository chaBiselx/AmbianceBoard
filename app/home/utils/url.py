import urllib
from django.conf import settings

def get_full_url(path):
    scheme = settings.APP_SCHEME
    host = settings.APP_HOST
    port = ''
    if(settings.APP_PORT):
        port = ':' + str(settings.APP_PORT)
    return f"{scheme}://{host}{port}{path}"

def redirection_url(url):
    scheme = settings.APP_SCHEME
    host = settings.APP_HOST
    port = ''
    if(settings.APP_PORT):
        port = ':' + str(settings.APP_PORT)
    allow_list = [f'{host}{port}']
    parsed_url = urllib.parse.urlparse(url)
    
    if(parsed_url.netloc == "" and parsed_url.scheme == ""):
        return url #relative url
    if parsed_url.netloc in allow_list and parsed_url.scheme == scheme:
        return f"{scheme}://" + parsed_url.netloc
    return "/"