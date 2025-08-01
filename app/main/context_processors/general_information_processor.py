from django.http import HttpRequest, HttpResponse
from main.service.GeneralNotificationService import GeneralNotificationService
from main.utils.ServerNotificationBuilder import ServerNotificationBuilder


def general_information_processor(request):
    # Liste des URLs où la sidebar doit apparaître
    general_notifications = GeneralNotificationService(request.user).get_list_notifications()
    for notification in general_notifications:
        print(f"Notification: {notification.message}, Class: {notification.class_name}")
        
        ServerNotificationBuilder(request).set_message(notification.message).set_statut(notification.class_name).send()
    return {}