from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from apps.game.ws_game import WebSocketGame
from apps.game.ws_match import MatchMaking

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ HTTP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
urlpatterns = [
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ PAGES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    path('pages/', include("apps.pages.urls")),
    path('pong/', include('apps.pong.urls')),
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ API ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    path('api/auth/', include('apps.auth.api.urls')),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ BASE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    re_path(r'^.*$', TemplateView.as_view(template_name='base.html')),

    # path('api/', include("apps.api.urls")),
    # path('api/auth/', include('apps.auth.api.urls')),
    # path('api/profile/', include('apps.profile.api.urls')),
    # path('api/client/', include('apps.shared.api.urls'))
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ WEBSOCKET ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

websocket_urlpatterns = [
    path("ws/game/matchmaking/", MatchMaking.as_asgi()),
    re_path(r"ws/game/(?P<room_name>\w+)/$", WebSocketGame.as_asgi())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)