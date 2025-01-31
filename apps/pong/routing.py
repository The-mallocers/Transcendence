from django.urls import path, re_path

from apps.game.models import GameRoom
from apps.pong import consumers

websocket_urlpatterns = [
    path('ws/somepath/', consumers.MyConsumer.as_asgi()),
    re_path(r"ws/game/(?P<room_name>\w+)/$", GameRoom.as_asgi()),
]
