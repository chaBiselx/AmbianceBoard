from django.http import HttpRequest, HttpResponse
from main.domain.common.service.GeneralNotificationService import GeneralNotificationService
from main.domain.common.utils.ServerNotificationBuilder import ServerNotificationBuilder
from django.urls import reverse
from main.domain.common.utils.settings import Settings
from main.architecture.persistence.repository.AsyncDownloadJobRepository import AsyncDownloadJobRepository
from main.domain.common.utils.cache.CacheFactory import CacheFactory
from main.domain.private.service.LinkService import LinkService



def __get_has_recent_async_download_jobs(request) -> bool:
    """Retourne True si l'utilisateur a des jobs asynchrones récents (24h)."""
    if not request.user.is_authenticated:
        return False

    cache = CacheFactory.get_default_cache()
    cache_key = f"{LinkService.PREFIX_CACHE_NAVBAR}{request.user.id}"
    cached_value = cache.get(cache_key)

    if cached_value is not None:
        return bool(cached_value)

    has_recent_async_download_jobs = AsyncDownloadJobRepository().count_recent_jobs_for_user(request.user) > 0
    cache.set(cache_key, has_recent_async_download_jobs, timeout=5 * 60)  # Cache pour 5 minutes
    return has_recent_async_download_jobs


def general_information_processor(request):
    # Liste des URLs où la sidebar doit apparaître
    general_notifications = GeneralNotificationService(request.user).get_list_notifications()
    for notification in general_notifications:
        server_notification = ServerNotificationBuilder(request)\
            .set_message(notification.message)\
            .set_statut(notification.class_name)\
            .add_meta("uuid", str(notification.uuid))
        if request.user.is_authenticated:
            server_notification.add_meta("url_dismiss", reverse("dismissGeneralNotification", args=[notification.uuid]))

        server_notification.send()


    has_recent_async_download_jobs = __get_has_recent_async_download_jobs(request)
    
    return {
        'APP_ENV': Settings.get('APP_ENV'),
        'DEBUG': Settings.get('DEBUG', False),
        'GRAFANA_URL': Settings.get('GRAFANA_URL', ''),
        'has_recent_async_download_jobs': has_recent_async_download_jobs,
    }