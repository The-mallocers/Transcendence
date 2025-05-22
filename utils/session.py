import logging
import traceback
from datetime import datetime
from time import sleep

from django.http import HttpRequest, JsonResponse
from rest_framework import status

from apps.client.models import Clients
from config import settings
from utils.enums import RTables, JWTType, SessionType, ResponseError, EventType
from utils.jwt.JWT import JWT
from utils.redis import RedisConnectionPool
from utils.websockets.channel_send import send_group_error


class SessionLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis = RedisConnectionPool.get_sync_connection(self.__class__.__name__)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _store_session_redis(self, request: HttpRequest, client):
        # Store session settings in redis
        access = JWT.extract_token(request, JWTType.ACCESS)
        refresh = JWT.extract_token(request, JWTType.REFRESH)

        self.redis.hset(RTables.HASH_CLIENT_SESSION(client.id), SessionType.SESSION_KEY, access.SESSION_KEY)
        self.redis.hset(RTables.HASH_CLIENT_SESSION(client.id), SessionType.IP_ADRESS, access.IP_ADDRESS)
        self.redis.hset(RTables.HASH_CLIENT_SESSION(client.id), SessionType.USER_AGENT, access.USER_AGENT)
        self.redis.hset(RTables.HASH_CLIENT_SESSION(client.id), SessionType.FINGERPRINT, access.DEVICE_FINGERPRINT)
        self.redis.hset(RTables.HASH_CLIENT_SESSION(client.id), SessionType.LAST_ACTIVITY, int(datetime.now().timestamp()))
        self.redis.hset(RTables.HASH_CLIENT_SESSION(client.id), SessionType.LAST_JWT_ACCESS, access.encode_token())
        self.redis.hset(RTables.HASH_CLIENT_SESSION(client.id), SessionType.LAST_JWT_REFRESH, refresh.encode_token())
        self.redis.expire(RTables.HASH_CLIENT_SESSION(client.id), settings.SESSION_LIMITING_EXPIRY)

    def _check_session(self, request: HttpRequest, client):
        current_session_key = request.session.session_key
        stored_session_key_encode = self.redis.hget(RTables.HASH_CLIENT_SESSION(client.id), SessionType.SESSION_KEY)
        stored_session_key = None if stored_session_key_encode is None else stored_session_key_encode.decode()

        if stored_session_key and current_session_key != stored_session_key:
            request.session.flush()
            notification_channel = self.redis.hget(RTables.HASH_CLIENT(client.id), str(EventType.NOTIFICATION.value))
            if notification_channel:
                self.redis.hdel(RTables.HASH_CLIENT(client.id), str(EventType.NOTIFICATION.value))
                self.redis.delete(RTables.GROUP_NOTIF(client.id))

            tournament_channel = self.redis.hget(RTables.HASH_CLIENT(client.id), str(EventType.TOURNAMENT.value))
            if tournament_channel:
                self.redis.hdel(RTables.HASH_CLIENT(client.id), str(EventType.TOURNAMENT.value))
                self.redis.delete(RTables.GROUP_TOURNAMENT(client.id))

            send_group_error(RTables.GROUP_CLIENT(client.id), ResponseError.SESSION_EXPIRED, close=True)

            jwt_access_token_encode = self.redis.hget(RTables.HASH_CLIENT_SESSION(client.id), SessionType.LAST_JWT_ACCESS)
            jwt_refresh_token_encode = self.redis.hget(RTables.HASH_CLIENT_SESSION(client.id), SessionType.LAST_JWT_REFRESH)
            jwt_access_token = jwt_access_token_encode.decode('utf-8')
            jwt_refresh_token = jwt_refresh_token_encode.decode('utf-8')
            jwt_access_payload = JWT.decode_token(jwt_access_token)
            jwt_refresh_payload = JWT.decode_token(jwt_refresh_token)
            jwt_access = JWT.get_token(jwt_access_payload)
            jwt_refresh = JWT.get_token(jwt_refresh_payload)
            jwt_access.invalidate_token()
            jwt_refresh.invalidate_token()

            return


    def __call__(self, request: HttpRequest):
        if request.session.session_key is None:
            request.session.create()

        if not request.user.is_authenticated:
            return self.get_response(request)

        for path in settings.SESSION_LIMITING_EXEMPT_PATHS:
            if request.path.startswith(path):
                return self.get_response(request)

        # if request.headers.get('upgrade', '').lower() == 'websocket':
        #     print('test')
        #     return self.get_response(request)

        try:
            client = Clients.get_client_by_request(request)

            self._check_session(request, client)

            if not self.redis.exists(RTables.HASH_CLIENT_SESSION(client.id)):
                self._store_session_redis(request, client)

            return self.get_response(request)
        except Exception as e:
            return JsonResponse({
                'status': 'unauthorized',
                'redirect': '/auth/login',
                'message': str(e)}, status=status.HTTP_302_FOUND)
