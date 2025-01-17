"""
ASGI config for Transcendence project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pong.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Transcendence.settings')

# Initialize Django ASGI application early to ensure the app registry is loaded.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

# We're doing a lot here, but the idea is that we are setting up asgi, when
# we will want to access a page, as in the http protocol, we will return our basic django app
# but if we are trying to connect a websocket, we will go to the url patterns
# as defined in the routing.py of the app we are currently using.
