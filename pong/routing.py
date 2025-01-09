from django.urls import path
from . import consumers

#ws/pong to signify its a websocket thing, im not expecting the user to
#type ws/pong in his search bar.
websocket_urlpatterns = [
    path('ws/pong/', consumers.PongConsumer.as_asgi()),
]
