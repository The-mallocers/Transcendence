from django.urls import path
from pong import consumers

websocket_urlpatterns = [
    path('ws/somepath/', consumers.MyConsumer.as_asgi()),
]