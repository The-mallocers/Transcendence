import jwt
from django.http import HttpRequest
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.shared.models import Clients
from utils.jwt.JWT import JWTType, JWT
from utils.jwt.JWTGenerator import JWTGenerator


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        jwt_key = auth_header.split(" ")[1]

        try:
            jwt_token: JWT = JWTGenerator.validate_token(jwt_key, JWTType.ACCESS)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        sub = jwt_token.SUB
        if not sub:
            AuthenticationFailed("Invalid payload")

        client: Clients = Clients.get_client_by_id(jwt_token.SUB)
        if not client:
            raise AuthenticationFailed("User not found")
        else:
            return client, jwt_key
