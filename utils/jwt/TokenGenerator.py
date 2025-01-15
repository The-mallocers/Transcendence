import uuid
from datetime import datetime, timezone, timedelta

import jwt
from django.conf import settings

from shared.models import Clients


class TokenGenerator:
    def __init__(self):
        self.secret_key = getattr(settings, 'JWT_SECRET_KEY')
        self.issuer = "https://api.transcendence.fr"

    def generate_access_token(self, user_id: Clients.id) -> str:
        now = datetime.now(tz=timezone.utc)

        payload = {
            #     Token clains for standars jwt
            'iss': self.issuer,
            'sub': str(user_id),
            'jti': str(uuid.uuid4()),  # JWT id

            #     Time life
            'iat': now,  # Time delivered
            'exp': now + timedelta(minutes=settings.JWT_EXP_ACCESS_TOKEN),

            #     Token type
            'type': 'access',

            #     Necessary informations for auth
            'roles': [
                'client'
            ],
            'permissions': None,

            #     Security context
            'device_id': None,
            'ip_address': None,
            'user_agent': None
        }

        headers = {
            'typ': 'JWT',
            'alg': 'HS256',
            'kid': 'access-key-1'
        }

        return jwt.encode(payload, self.secret_key, algorithm='HS256',
                          headers=headers)

    def generate_refresh_token(self, user_id: Clients.id) -> str:
        now = datetime.now(tz=timezone.utc)

        payload = {
            #     Token clains for standars jwt
            "iss": self.issuer,
            "sub": str(user_id),
            "jti": str(uuid.uuid4()),

            #     Long time life
            "iat": now,
            "exp": now + timedelta(days=30),

            #     Token type
            "type": "refresh",

            #     Security context
            "device_id": None,
            "device_fingerprint": None,

            #     Token version for revoked if ncessary
            "token_version": None
        }

        headers = {
            "typ": "JWT",
            "alg": "HS256",
            "kid": "refresh-key-1"
        }

        return jwt.encode(payload, self.secret_key, algorithm='HS256',
                          headers=headers)
