import uuid
from datetime import timezone, datetime, timedelta
from enum import Enum

from django.conf import settings

from apps.shared.models import Clients


class JWTType(str, Enum):
    ACCESS: str = 'access'
    REFRESH: str = 'refresh'


class JWT:
    def __init__(self, client: Clients, token_type: JWTType):
        self.EXP = None
        self.client: Clients = client
        self.issuer = "https://api.transcendence.fr"
        now = datetime.now(tz=timezone.utc)

        self.ISS: str = self.issuer
        self.SUB: Clients.id = client.id
        self.JTI: uuid.UUID = uuid.uuid4()

        self.IAT = now
        if token_type == JWTType.ACCESS:
            self.EXP = now + timedelta(
                minutes=getattr(settings, 'JWT_EXP_ACCESS_TOKEN'))
        elif token_type == JWTType.REFRESH:
            self.EXP = now + timedelta(
                days=getattr(settings, 'JWT_EXP_REFRESH_TOKEN'))

        self.TYPE: JWTType = token_type

        self.ROLES: list[str] = ['client']
        if self.client.rights.is_admin:
            self.ROLES.append('admin')

        self.DEVICE_ID: str = ''
        self.IP_ADDRESS: str = ''
        self.USER_AGENT: str = ''
        self.DEVICE_FINGERPRINT: str = ''
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

        if self.TYPE == JWTType.ACCESS:
            token_dict['roles'] = self.ROLES
            token_dict['ip_address'] = self.IP_ADDRESS
            token_dict['user_agent'] = self.USER_AGENT

        if self.TYPE == JWTType.REFRESH:
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
