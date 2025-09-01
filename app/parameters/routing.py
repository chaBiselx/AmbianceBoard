from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from main.domain.sharedSoundboard.consummers.SharedSoundboardConsummers import SharedSoundboardConsummers


websocket_urlpatterns = [
    re_path(r'^shared/ws/(?P<soundboard_uuid>[\w-]+)/(?P<token>[\w-]+)$', SharedSoundboardConsummers.as_asgi()),
]


application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})

