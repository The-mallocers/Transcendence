import logging

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to ensure the app registry is loaded
django_asgi_app = get_asgi_application()
from config.urls import websocket_urlpatterns

logging.getLogger('daphne.cli').info("Starting server with ASGI")

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
