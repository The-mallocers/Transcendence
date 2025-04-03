import re

import jwt
from django.conf import settings
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect

from apps.client.models import Clients
from utils.enums import JWTType
from utils.jwt.JWT import JWT


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.secret_key = getattr(settings, 'JWT_SECRET_KEY')
        self.algorithm = getattr(settings, 'JWT_ALGORITH')

    def _in_excluded_path(self, path: str) -> bool:
        for excluded in settings.EXCLUDED_PATHS:
            if self._path_matches(excluded, path):
                return True
        return False

    def _get_required_roles(self, path: str):
        protected_paths = settings.ROLE_PROTECTED_PATHS
        for pattern, roles in protected_paths.items():
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
            response = set_cookie(access.token, response)
            response = set_cookie(refresh.token, response)

            return response
        except jwt.ExpiredSignatureError as e:
            raise jwt.ExpiredSignatureError(f'{str(e)}')
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f'{str(e)}')

    def __call__(self, request: HttpRequest):
        path = request.path_info
        print(path)

        #We only want to check if the request starts with pages (aka our spa did the fetch)
        #If it doesnt start with pages, it will just load base.html, and thats what we want
        if not path.startswith('/pages/'):
            return self.get_response(request)

        if self._in_excluded_path(path):
            print('excluded path')
            return self.get_response(request)

        try:
            print('try to extract token')
            access_token: JWT = JWT.extract_token(request, JWTType.ACCESS)
            request.access_token = access_token
            print('success extract token')

            required_roles = self._get_required_roles(path)
            if required_roles:
                if not any(role in access_token.ROLES for role in required_roles):
                    return HttpResponseRedirect('/')  # redirect with json response

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
                'message': 'Session expired'}, status=302)
        except Exception as e:
            return JsonResponse(
                {'error': f'Internal server error: {str(e)}'},
                status=500
            )
