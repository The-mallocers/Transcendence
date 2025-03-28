import jwt
from django.conf import settings
from django.http import HttpResponse, HttpRequest

from apps.shared.models import Clients
from utils.jwt.JWT import JWT, JWTType


class JWTGenerator:
    secret_key = getattr(settings, 'JWT_SECRET_KEY')
    algorithm = getattr(settings, 'JWT_ALGORITH')

    def __init__(self, client: Clients, token_type: JWTType):
        self.issuer = "https://api.transcendence.fr"
        self.token_key: str = ''
        self.token: JWT = JWT(client, token_type)

    def set_cookie(self, response: HttpResponse) -> HttpResponse:
        headers = {
            'typ': 'JWT',
            'alg': self.algorithm,
            'kid': 'access-key-1'
        }

        self.token_key = jwt.encode(self.token.get_payload(), self.secret_key,
                                    algorithm=self.algorithm, headers=headers)

        response.set_cookie(
            f'{self.token.TYPE.value}_token',
            f'{self.token_key}',
            httponly=True,
            secure=True,
            samesite='Lax',
        )

        return response

    @classmethod
    def extract_token(cls, request: HttpRequest,
                      token_type: JWTType) -> JWT | None:
        token_key = request.COOKIES.get(token_type.value + '_token')
        try:
            payload = jwt.decode(token_key, cls.secret_key,
                                 algorithms=[cls.algorithm])
            token: JWT = JWT.get_token(payload)
            return token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def validate_token(cls, token_key: str, token_type: JWTType) -> JWT:
        try:
            payload = jwt.decode(token_key, cls.secret_key,
                                 algorithms=[cls.algorithm])
            token = JWT.get_token(payload)
            if token.TYPE != token_type:
                raise jwt.InvalidKeyError(
                    f'Invalid token type: {token.TYPE}')
            return token
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError(f'Token {token_type} expired')
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f'Invalid {token_type} token: {str(e)}')
