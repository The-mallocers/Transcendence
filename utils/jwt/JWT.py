import hashlib
import uuid
from datetime import timedelta, datetime, timezone

import jwt
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.auth.models import InvalidatedToken
from apps.client.models import Clients
from utils.enums import JWTType, RTables, SessionType
from utils.redis import RedisConnectionPool
from utils.util import create_jti_id, get_client_ip


class JWT:
    def __init__(self, client: Clients, token_type: JWTType, request: HttpRequest = None):
        # ── Local Vars ────────────────────────────────────────────────────────────── #
        self.client: Clients = client
        now = datetime.now(tz=timezone.utc)

        # ── Jwt Settings ──────────────────────────────────────────────────────────── #
        self.EXP = None
        self.ISS: str = settings.JWT_ISS
        self.SUB: Clients.id = client.id
        self.JTI: uuid.UUID = create_jti_id()
        self.IAT = now
        self.TYPE: JWTType = token_type

        if token_type == JWTType.ACCESS:
            self.EXP = now + timedelta(
                minutes=int(settings.JWT_EXP_ACCESS_TOKEN))
        elif token_type == JWTType.REFRESH:
            self.EXP = now + timedelta(
                days=int(settings.JWT_EXP_REFRESH_TOKEN))

        self.ROLES: list[str] = ['client']
        if self.client.rights.is_admin:
            self.ROLES.append('admin')

        self.SESSION_KEY = request.session.session_key
        self.IP_ADDRESS = get_client_ip(request)
        self.USER_AGENT = request.META.get('HTTP_USER_AGENT', '')
        self.DEVICE_FINGERPRINT = hashlib.sha256(str(f"{self.USER_AGENT}|{self.IP_ADDRESS}").encode()).hexdigest()


    def __str__(self):
        return f"{self.TYPE}_token expired in {self.EXP}, issue a {self.IAT}"

    # ── Public ────────────────────────────────────────────────────────────────────── #

    def set_cookie(self, response: HttpResponse) -> HttpResponse:
        response.set_cookie(
            f'{self.TYPE.value}_token',
            f'{self.encode_token()}',
            httponly=True,
            secure=True,
            samesite='Lax',
            expires=self.EXP
        )
        self._store_session_redis()
        return response

    def invalidate_token(self):
        # Convert EXP to datetime if it's a timestamp
        exp_datetime = self.EXP
        if isinstance(self.EXP, (int, float)):
            exp_datetime = datetime.fromtimestamp(self.EXP, tz=timezone.utc)
        InvalidatedToken.objects.get_or_create(
            jti=self.JTI,
            token=self.encode_token(),
            exp=exp_datetime,
            type=self.TYPE
        )

    @staticmethod
    def validate_token(token_key: str, token_type: JWTType, request):
        token = None
        try:
            payload = JWT._decode_token(token_key)
            token = JWT._get_token(payload, request)
            if InvalidatedToken.objects.filter(jti=token.JTI).exists():
                raise jwt.InvalidKeyError('Token has been invalidated')
            if token and token.TYPE != token_type:
                raise jwt.InvalidTokenError(f'Validating token with type {token.TYPE} failed due to invalide token type.')
            return token
        except jwt.DecodeError as e:
            raise jwt.InvalidTokenError(f'Error decoding token, it is either invalid or expired. {str(e)}') 
        except jwt.ExpiredSignatureError as e:
            raise jwt.ExpiredSignatureError(f'Validating token with type {token_type.value} failed due to expired signature. {str(e)}')
        except (jwt.InvalidTokenError, jwt.DecodeError) as e:
            raise jwt.InvalidTokenError(f'Validating token with type {token_type.value} failed due to invalid token. {str(e)}')
        except jwt.InvalidKeyError as e:
            raise jwt.InvalidKeyError(f'Validating token with type {token_type.value} failed due to invalid key. {str(e)}')
        except Clients.DoesNotExist as e:
            raise jwt.InvalidKeyError('Token link to a non-existent user')

    @staticmethod
    def extract_token(request: HttpRequest, token_type: JWTType):
        token_key = request.COOKIES.get(token_type.value + '_token')
        return JWT.validate_token(token_key, token_type, request)

    def encode_token(self):
        header = {
            'alg': settings.JWT_ALGORITH,
            'typ': 'JWT',
            'kid': f'key-id-{str(self.JTI)}'
        }
        payload = self._get_payload()
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITH, headers=header)
        return token

    # ── Private ───────────────────────────────────────────────────────────────────── #

    def _get_payload(self):
        token_dict = {
            'iss': self.ISS,
            'sub': str(self.SUB),
            'jti': str(self.JTI),
            'iat': self.IAT,
            'exp': self.EXP,
            'type': self.TYPE,
            'session_id': self.SESSION_KEY,
            'ip_address': self.IP_ADDRESS,
            'user_agent': self.USER_AGENT,
            'device_fingerprint': self.DEVICE_FINGERPRINT,
        }

        if self.TYPE == JWTType.ACCESS:
            token_dict['roles'] = self.ROLES

        return token_dict

    def _store_session_redis(self):
        redis = RedisConnectionPool.get_sync_connection('JWT')

        # Store session settings in redis
        redis.hset(RTables.HASH_CLIENT_SESSION(self.client.id), SessionType.SESSION_ID, self.SESSION_KEY)
        redis.hset(RTables.HASH_CLIENT_SESSION(self.client.id), SessionType.IP_ADRESS, self.IP_ADDRESS)
        redis.hset(RTables.HASH_CLIENT_SESSION(self.client.id), SessionType.USER_AGENT, self.USER_AGENT)
        redis.hset(RTables.HASH_CLIENT_SESSION(self.client.id), SessionType.FINGERPRINT, self.DEVICE_FINGERPRINT)
        redis.hset(RTables.HASH_CLIENT_SESSION(self.client.id), SessionType.LAST_ACTIVITY, int(datetime.now().timestamp()))
        redis.expire(RTables.HASH_CLIENT_SESSION(self.client.id), settings.SESSION_LIMITING_EXPIRY)
        RedisConnectionPool.close_sync_connection('JWT')

    @staticmethod
    def _decode_token(token: str):
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITH])
        return payload

    @staticmethod
    def _get_token(data: dict, request):
        client = Clients.get_client_by_id(data['sub'])
        if client is None:
            raise Clients.DoesNotExist()
        token = JWT(client=client, token_type=data['type'], request=request)
        token.EXP = data.get('exp')
        token.JTI = uuid.UUID(data['jti'])
        token.IAT = data.get('iat')
        token.ROLES = data.get('roles', [])
        token.SESSION_KEY = data.get('session_id')
        token.IP_ADDRESS = data.get('ip_address')
        token.USER_AGENT = data.get('user_agent')
        token.DEVICE_FINGERPRINT = data.get('device_fingerprint')
        return token
