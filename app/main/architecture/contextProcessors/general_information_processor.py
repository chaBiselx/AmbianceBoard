from django.http import HttpRequest, HttpResponse
from main.service.GeneralNotificationService import GeneralNotificationService
from main.domain.common.utils.ServerNotificationBuilder import ServerNotificationBuilder
from django.urls import reverse


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
    return {}