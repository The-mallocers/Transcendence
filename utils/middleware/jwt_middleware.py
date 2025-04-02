import re

import jwt
from django.conf import settings
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect

from apps.client.models import Clients
from utils.jwt.JWTGenerator import JWTType, JWT, JWTGenerator


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.secret_key = getattr(settings, 'JWT_SECRET_KEY')
        self.algorithm = getattr(settings, 'JWT_ALGORITH')
        self.protected_paths = getattr(settings, 'PROTECTED_PATHS')
        self.excluded_paths = getattr(settings, 'EXCLUDED_PATHS')
        self.role_protected_paths = getattr(settings, 'ROLE_PROTECTED_PATHS')

    def _should_check_path(self, path: str) -> bool:
        if path.startswith('/pages/') == False and path.startswith('/api/') == False:
            return False
        for excluded in self.excluded_paths:
            if self._path_matches(excluded, path):
                return False

        for protected in self.protected_paths:
            if self._path_matches(protected, path):
                return True
        return False

    def _get_required_roles(self, path: str):
        for pattern, roles in self.role_protected_paths.items():
            if self._path_matches(pattern, path):
                return roles
        return None

    def _path_matches(self, pattern, path: str) -> bool:
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.match(f'^{regex_pattern}$', path))

    def _extract_access_token(self, request: HttpRequest) -> str:
        token_key: str = request.COOKIES.get('access_token')
        if token_key is None:
            raise jwt.InvalidKeyError(f'Token missing')
        return token_key

    def _extract_refresh_token(self, request: HttpRequest) -> str:
        token_key: str = request.COOKIES.get('refresh_token')
        if token_key is None:
            raise jwt.InvalidKeyError(f'Token missing')
        return token_key

    def _refresh_token(self, request: HttpRequest):
        try:
            refresh_token: JWT = JWTGenerator.validate_token(
                self._extract_refresh_token(request), JWTType.REFRESH)

            client: Clients = Clients.get_client_by_id(refresh_token.SUB)

            access = JWTGenerator(client, JWTType.ACCESS)
            refresh = JWTGenerator(client, JWTType.REFRESH)

            request.COOKIES['access_token'] = access.token_key
            request.COOKIES['refresh_token'] = refresh.token_key
            request.access_token = access.token

            response = self.get_response(request)
            response = access.set_cookie(response)
            response = refresh.set_cookie(response)

            return response
        except jwt.ExpiredSignatureError as e:
            raise jwt.ExpiredSignatureError(f'{str(e)}')
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f'{str(e)}')

    def __call__(self, request: HttpRequest):
        path = request.path_info

        if not self._should_check_path(path):
            return self.get_response(request)

        try:
            token_key: str = self._extract_access_token(request)
            token: JWT = JWTGenerator.validate_token(token_key, JWTType.ACCESS)

            request.access_token = token

            required_roles = self._get_required_roles(path)
            if required_roles:
                if not any(role in token.ROLES for role in required_roles):
                    return HttpResponseRedirect('/')
            return self.get_response(request)
        except jwt.ExpiredSignatureError:
            try:
                return self._refresh_token(request)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidKeyError):
                return JsonResponse({
                    'status': 'unauthorized',
                    'redirect': '/auth/login',
                    'message': 'Session expired'}, status=302)
        except (jwt.InvalidTokenError, jwt.InvalidKeyError):
            return JsonResponse({
                'status': 'unauthorized',
                'redirect': '/auth/login',
                'message': 'Invalid authentication'}, status=302)
        except Exception as e:
            return JsonResponse(
                {'error': f'Internal server error: {str(e)}'},
                status=500
            )
