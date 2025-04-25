"""
ASGI config for Transcendence project.

It exposes the ASGI callable as a module-level variable named `application`.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import logging
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.utils.log import configure_logging

# Configure Django's logging
configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
logger = logging.getLogger('django.server')

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application
logger.info('Initializing ASGI application')
django_asgi_app = get_asgi_application()

# Import websocket URL patterns after Django is initialized
from config.urls import websocket_urlpatterns

# Define the ASGI application
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
