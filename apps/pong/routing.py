from django.urls import path
from apps.pong import consumers

websocket_urlpatterns = [
    path('ws/somepath/', consumers.MyConsumer.as_asgi()),
]
