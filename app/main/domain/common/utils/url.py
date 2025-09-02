import urllib
from main.domain.common.utils.settings import Settings


def get_full_url(path: str) -> str:
    scheme = Settings.get('APP_SCHEME')
    host = Settings.get('APP_HOST')
    port = ''
    if(Settings.get('APP_PORT') and Settings.get('APP_ENV') == 'prod'):
        port = ':' + str(Settings.get('APP_PORT'))
    return f"{scheme}://{host}{port}{path}"

def redirection_url(url: str) -> str:
    scheme = Settings.get('APP_SCHEME')
    host = Settings.get('APP_HOST')
    port = ''
    if(Settings.get('APP_PORT') and Settings.get('APP_ENV') == 'prod'):
        port = ':' + str(Settings.get('APP_PORT'))
    allow_list = [f'{host}{port}']
    parsed_url = urllib.parse.urlparse(url)
    
    if(parsed_url.netloc == "" and parsed_url.scheme == ""):
        return url #relative url
    if parsed_url.netloc in allow_list and parsed_url.scheme == scheme:
        return f"{scheme}://" + parsed_url.netloc
    return "/"