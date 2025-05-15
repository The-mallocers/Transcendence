import hashlib
import logging

from django.conf import settings
from django.http import HttpRequest

from utils.redis import RedisConnectionPool


class SessionLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.session_expiry = settings.SESSION_LIMITING_EXPIRY
        self.redis = RedisConnectionPool.get_sync_connection(self.__class__.__name__)
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_fingerprint(self, request: HttpRequest):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_addres = self.get_client_ip(request)

        fingerprint_base = f"{user_agent}|{ip_addres}"
        fingerprint = hashlib.sha256(fingerprint_base.encode()).hexdigest()
        return fingerprint

    def get_client_ip(self, request: HttpRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def __call__(self, request: HttpRequest):
        print(request.user.is_authenticated)
        print(request.user.is_staff)

        if not self.redis:
            self.logger.warning('Redis not avaible, skipping session limiting')
            return self.get_response(request)

        if not request.user.is_authenticated:
            return self.get_response(request)

        if settings.SESSION_LIMITING_EXEMPT_ADMIN and request.user.is_staff:
            return self.get_response(request)

        return self.get_response(request)