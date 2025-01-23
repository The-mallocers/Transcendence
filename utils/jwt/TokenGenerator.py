import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

import jwt
from django.conf import settings
from django.http import HttpResponse, HttpRequest

from Transcendence import settings
from shared.models import Clients


@dataclass
class TokenType:
    ACCESS: str = str('access')
    REFRESH: str = str('refresh')


class Token:
    def __init__(self, client: Clients, token_type: str):
        self.EXP = None
        self.client: Clients = client
        self.issuer = "https://api.transcendence.fr"
        now = datetime.now(tz=timezone.utc)

        self.ISS: str = self.issuer
        self.SUB: Clients.id = client.id
        self.JTI: uuid.UUID = uuid.uuid4()

        self.IAT = now
        if token_type == str(TokenType.ACCESS):
            self.EXP = now + timedelta(
                seconds=getattr(settings, 'JWT_EXP_ACCESS_TOKEN'))
        elif token_type == str(TokenType.REFRESH):
            self.EXP = now + timedelta(
                seconds=getattr(settings, 'JWT_EXP_REFRESH_TOKEN'))

        self.TYPE: str = token_type

        self.ROLES: list[str] = ['client']
        if self.client.rights.is_admin:
            self.ROLES.append('admin')

        self.DEVICE_ID: str = None
        self.IP_ADDRESS: str = None
        self.USER_AGENT: str = None
        self.DEVICE_FINGERPRINT: str = None
        self.TOKEN_VERSION: int = 0

    def __str__(self):
        return f"{self.TYPE}_token expired in {self.EXP}, issue a {self.IAT}"

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
            token_dict['ip_address'] = self.IP_ADDRESS
            token_dict['user_agent'] = self.USER_AGENT

        if self.TYPE == TokenType.REFRESH:
            token_dict['device_fingerprint'] = self.DEVICE_FINGERPRINT
            token_dict['token_version'] = self.TOKEN_VERSION

        return token_dict

    @classmethod
    def get_token(cls, data: dict):
        client = Clients.get_client_by_id(data['sub'])
        token = cls(
            client=client,
            token_type=data['type']
        )
        # Remplissage des autres attributs
        token.EXP = data.get('exp')
        token.JTI = uuid.UUID(data['jti'])
        token.IAT = data.get('iat')
        token.ROLES = data.get('roles', [])
        token.DEVICE_ID = data.get('device_id')
        token.IP_ADDRESS = data.get('ip_address')
        token.USER_AGENT = data.get('user_agent')
        token.DEVICE_FINGERPRINT = data.get('device_fingerprint')
        token.TOKEN_VERSION = data.get('token_version', 0)
        return token


class TokenGenerator:
    secret_key = getattr(settings, 'JWT_SECRET_KEY')
    algorithm = getattr(settings, 'JWT_ALGORITH')

    def __init__(self, client: Clients, token_type: str):
        self.issuer = "https://api.transcendence.fr"
        self.token_key: str = ''
        self.token: Token = Token(client, token_type)

    def set_cookie(self, response: HttpResponse) -> HttpResponse:
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
            samesite='Lax',
        )

        return response

    @classmethod
    def extract_token(cls, request: HttpRequest,
                      token_type: TokenType) -> Token | None:
        token_key = request.COOKIES.get(str(token_type) + '_token')
        try:
            payload = jwt.decode(token_key, cls.secret_key,
                                 algorithms=[cls.algorithm])
            token: Token = Token.get_token(payload)
            return token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
