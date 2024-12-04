from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from home.views.general.views import home, create_account, login_view, logout_view
from home.views.Soundboard.views import soundboard_list, soundboard_create, soundboard_read, soundboard_update, soundboard_delete

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    
    path("create-account/", create_account, name="createAccount"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    
    path("soundBoards/", soundboard_list, name="soundboardsList"),
    path("soundBoards/new", soundboard_create, name="soundboardsNew"),
    path("soundBoards/<int:soundboard_id>", soundboard_read, name="soundboardsRead"),
    path("soundBoards/<int:soundboard_id>/update", soundboard_update, name="soundboardsUpdate"),
    path("soundBoards/<int:soundboard_id>/delete", soundboard_delete, name="soundboardsDelete"),
    
    
]


if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
