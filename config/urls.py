from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from utils.enums import EventType
from utils.websockets.consumers.chat import ChatConsumer
from utils.websockets.consumers.game import GameConsumer
from utils.websockets.consumers.notification import NotificationfConsumer
from utils.websockets.consumers.tournament import TournamentConsumer
from django.views.static import serve



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HTTP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
urlpatterns = [
    path('pages/', include("config.pages")),  # Html view path
    path('api/auth/', include('apps.auth.api.urls')),
    path('api/friends/', include('apps.notifications.api.urls')),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^.*$', TemplateView.as_view(template_name='base.html')),
    # Default view
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ WEBSOCKET ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
websocket_urlpatterns = [
    path(f"ws/{EventType.GAME.value}/", GameConsumer.as_asgi()),
    path(f"ws/{EventType.CHAT.value}/", ChatConsumer.as_asgi()),
    path(f"ws/{EventType.TOURNAMENT.value}/", TournamentConsumer.as_asgi()),
    path(f"ws/{EventType.NOTIFICATION.value}/", NotificationfConsumer.as_asgi())
]

#leaving this here because i was using this for debug
# *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
