from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from home.views.general.views import home
from home.views.general.views import final_user_view
from home.views.soundboard.views import soundboard_list, soundboard_create,soundboard_read,soundboard_update, soundboard_delete

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("soundBoards/", soundboard_list, name="soundboardsList"),
    path("soundBoards/new", soundboard_create, name="soundboardsNew"),
    path("soundBoards/<int:soundboard_id>", soundboard_read, name="soundboardsRead"),
    path("soundBoards/<int:soundboard_id>/update", soundboard_update, name="soundboardsUpdate"),
    path("soundBoards/<int:soundboard_id>/delete", soundboard_delete, name="soundboardsDelete"),
    path('final-user/', final_user_view, name="final_user_view"),
    
    
]


if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
