import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

import jwt
from django.conf import settings
from django.http import HttpResponse

from Transcendence import settings
from shared.models import Clients


@dataclass
class TokenType:
    ACCESS: str = str('access')
    REFRESH: str = str('refresh')


class Token:
    def __init__(self, client: Clients, exp: int, token_type: str):
        self.client: Clients = client
        self.issuer = "https://api.transcendence.fr"
        now = datetime.now(tz=timezone.utc)

        self.ISS: str = self.issuer
        self.SUB: Clients.id = client.id
        self.JTI: uuid.UUID = uuid.uuid4()

        self.IAT = now
        self.EXP = 0
        if token_type is TokenType.ACCESS:
            self.EXP = now + timedelta(minutes=exp)
        elif token_type is TokenType.REFRESH:
            self.EXP = now + timedelta(days=exp)

        self.TYPE: str = token_type

        self.ROLES: list[str] = [
            'client'
        ]
        self.PERMISSIONS: list[str] = None

        self.DEVICE_ID: str = None
        self.IP_ADDRESS: str = None
        self.USER_AGENT: str = None
        self.DEVICE_FINGERPRINT: str = None
        self.TOKEN_VERSION: int = 0

    def get_payload(self):
        token_dict = {
            'iss': self.ISS,
            'sub': str(self.SUB),
            'jti': str(self.JTI),
            'iat': self.IAT,
            'exp': self.EXP,
            'type': self.TYPE,
            'device_id': self.DEVICE_ID
        }

        if self.TYPE == TokenType.ACCESS:
            token_dict['roles'] = self.ROLES
            token_dict['permission'] = self.PERMISSIONS
            token_dict['ip_address'] = self.IP_ADDRESS
            token_dict['user_agent'] = self.USER_AGENT

        if self.TYPE == TokenType.REFRESH:
            token_dict['device_fingerprint'] = self.DEVICE_FINGERPRINT
            token_dict['token_version'] = self.TOKEN_VERSION

        return token_dict

    @classmethod
    def get_token(cls, data: dict):
        exp = data['exp']
        client = Clients(id=data['sub'])
        token = cls(
            client=client,
            exp=exp,  # calcul de la durée d'expiration en minutes
            token_type=data['type']
        )
        # Remplissage des autres attributs
        token.JTI = uuid.UUID(data['jti'])
        token.IAT = data.get('iat')
        token.ROLES = data.get('roles', [])
        token.PERMISSIONS = data.get('permission', [])
        token.DEVICE_ID = data.get('device_id')
        token.IP_ADDRESS = data.get('ip_address')
        token.USER_AGENT = data.get('user_agent')
        token.DEVICE_FINGERPRINT = data.get('device_fingerprint')
        token.TOKEN_VERSION = data.get('token_version', 0)
        return token

class TokenGenerator:
    def __init__(self, client: Clients, token_type: str):
        self.secret_key = getattr(settings, 'JWT_SECRET_KEY')
        self.algorithm = getattr(settings, 'JWT_ALGORITH')
        self.issuer = "https://api.transcendence.fr"
        self.token_key: str = ''
        if token_type is TokenType.ACCESS:
            self.exp = getattr(settings, 'JWT_EXP_ACCESS_TOKEN')
        if token_type is TokenType.REFRESH:
            self.exp = getattr(settings, 'JWT_EXP_REFRESH_TOKEN')
        self.token: Token = Token(client, int(self.exp), token_type)

    def set_cookie(self, response: HttpResponse):
        headers = {
            'typ': 'JWT',
            'alg': self.algorithm,
            'kid': 'access-key-1'
        }

        self.token_key = jwt.encode(self.token.get_payload(), self.secret_key,
                                    algorithm=self.algorithm, headers=headers)

        response.set_cookie(
            f'{self.token.TYPE}_token',
            f'{self.token_key}',
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        return response
