import hashlib
import logging
import time

from django.conf import settings
from django.http import HttpRequest, HttpResponseForbidden

from utils.enums import RTables, SessionType
from utils.redis import RedisConnectionPool


class SessionLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.session_expiry = settings.SESSION_LIMITING_EXPIRY
        self.redis = RedisConnectionPool.get_sync_connection(self.__class__.__name__)
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_fingerprint(self, request: HttpRequest):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = self.get_client_ip(request)

        fingerprint_base = f"{user_agent}|{ip_address}"
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
        if not self.redis:
            self.logger.warning('Redis not avaible, skipping session limiting')
            return self.get_response(request)

        if not request.user.is_authenticated:
            return self.get_response(request)

        if not request.session.session_key:
            request.session.create()

        if settings.SESSION_LIMITING_EXEMPT_ADMIN and request.user.is_staff:
            return self.get_response(request)

        for path in settings.SESSION_LIMITING_EXEMPT_PATHS:
            if request.path.startswith(path):
                return self.get_response(request)

        redis_key = RTables.HASH_CLIENT_SESSION(request.user.id)

        new_fingerprint = self.generate_fingerprint(request)
        new_session_id = request.session.session_key

        has_active_session = self.redis.hexists(redis_key, SessionType.SESSION_ID)

        if has_active_session:
            # Parse stored session data
            old_fingerprint = self.redis.hget(redis_key, SessionType.FINGERPRINT)
            old_session_id = self.redis.hget(redis_key, SessionType.SESSION_ID)

            # If this is a different browser but the same user
            if old_fingerprint.decode('utf-8') != new_fingerprint or old_session_id != new_session_id:
                self.logger.warning(f"Multiple session attempt by user {request.user.id} - "
                                    f"Existing: {old_fingerprint.decode('utf-8')}, Current: {new_fingerprint}")

                # Choose what to do: block new session or invalidate old session
                if settings.SESSION_LIMITING_BLOCK_NEW:
                    print('blocked')
                    # Block the new session
                    return HttpResponseForbidden("You already have an active session in another browser. "
                                                 "Please log out from there before logging in here.")
                else:
                    # Allow new session to replace old one
                    self.logger.info(f"Replacing old session for user {request.user.id}")
                    # Continue to update Redis with the new session info below

            # Store or update the session information in Redis
        session_data = {
            SessionType.FINGERPRINT.value: new_fingerprint,
            SessionType.SESSION_ID.value: new_session_id,
            SessionType.LAST_ACTIVITY.value: int(time.time()),
            SessionType.USER_AGENT.value: request.META.get('HTTP_USER_AGENT', ''),
            SessionType.IP.value: self.get_client_ip(request)
        }

        self.redis.hset(redis_key, mapping=session_data)
        self.redis.expire(redis_key, self.session_expiry)

        # Update activity timestamp on subsequent requests
        if request.method == 'GET':
            self.redis.hset(redis_key, SessionType.LAST_ACTIVITY, int(time.time()))
            self.redis.expire(redis_key, self.session_expiry)

        response = self.get_response(request)

        if not request.session.session_key and hasattr(request, 'session'):
            request.session.save()

        return response
