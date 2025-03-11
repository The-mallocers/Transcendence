from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from utils.websockets.websocket import WebSocket

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HTTP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
urlpatterns = [
    path('pages/', include("apps.pages.urls")),
    path('api/auth/', include('apps.auth.api.urls')),
    # path('api/chat/', include('apps.auth.chat.urls')),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT), #I need this before the catch all so I can correctly serve media files (QRcode for two FA), its not "production ready", too bad !
    re_path(r'^.*$', TemplateView.as_view(template_name='base.html')),
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ WEBSOCKET ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
websocket_urlpatterns = [
    path("ws/game/", WebSocket.as_asgi()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)