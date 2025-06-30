from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from home.channels.SharedSoundboard import SharedSoundboard


websocket_urlpatterns = [
    re_path(r'^shared/ws/(?P<soundboard_uuid>[\w-]+)/(?P<token>[\w-]+)$', SharedSoundboard.as_asgi()),
]


application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})

