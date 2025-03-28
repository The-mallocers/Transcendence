from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from utils.websockets.consumers.chat import ChatConsumer
from utils.websockets.consumers.game import GameConsumer
from utils.websockets.consumers.tournament import TournamentConsumer

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HTTP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
urlpatterns = [
    path('pages/', include("config.pages")),  # Html view path
    path('api/auth/', include('apps.auth.api.urls')),  # Api path

    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    # I need this before the catch all so I can correctly serve media files (QRcode for two FA), its not "production ready", too bad !
    re_path(r'^.*$', TemplateView.as_view(template_name='base.html')),
    # Default view
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ WEBSOCKET ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
websocket_urlpatterns = [
    path("ws/game/", GameConsumer.as_asgi()),
    path("ws/chat/", ChatConsumer.as_asgi()),
    path("ws/tournaments/", TournamentConsumer.as_asgi())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
