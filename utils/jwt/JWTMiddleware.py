import fnmatch

import jwt
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from ipware import get_client_ip
from rest_framework import status

from apps.client.models import Clients
from utils.enums import JWTType, RTables, ConnectionType
from utils.jwt.JWT import JWT
from utils.redis import RedisConnectionPool


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis = RedisConnectionPool.get_sync_connection(alias=self.__class__.__name__)

    def _in_excluded_path(self, path: str) -> bool:
        if self.is_path_matching(path, settings.EXCLUDED_PATHS):
            return True
        return False

    def _get_required_roles(self, path: str):
        protected_paths = settings.ROLE_PROTECTED_PATHS
        for pattern, roles in protected_paths.items():
            if self.is_path_matching(path, [pattern]):
                return roles
        return None

    @staticmethod
    def is_path_matching(path, path_list):
        path = path.rstrip('/') if path != '/' else path
        normalized_path_list = [pattern.rstrip('/') for pattern in path_list]

        for pattern in normalized_path_list:
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path + '/', pattern):
                return True
        return False

    def _update_tokens(self, request: HttpRequest):
        refresh_token = JWT.extract_token(request, JWTType.REFRESH)  # if refresh is oudated, this will throw an exception
        client = Clients.get_client_by_id(refresh_token.SUB)

        new_access_token = JWT(client, JWTType.ACCESS)
        request.COOKIES['access_token'] = new_access_token.encode_token()

        request.user.is_authenticated = True
        request.user.is_staff = True if client.rights.is_admin else False
        
        response = self.get_response(request)
        new_access_token.set_cookie(response)
        return response

    def __call__(self, request: HttpRequest):
        #Create a custom user object for the request
        request.user = type('User', (), {
            'is_authenticated': False,
            'is_staff': False,
            'client': None
        })()

        #If the path is not protected
        if not self.is_path_matching(request.path_info, settings.PROTECTED_PATHS):
            return self.get_response(request)

        elif self.is_path_matching(request.path_info, settings.PROTECTED_PATHS):
            #If the path is excluded of protected_path
            if self._in_excluded_path(request.path_info):
                return self.get_response(request)
            else:
                try:  # let pass the request
                    token = JWT.extract_token(request, JWTType.ACCESS)
                    request.user.is_authenticated = True
                    request.user.is_staff = True if token.client.rights.is_admin else False
                    return self.get_response(request)
                except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
                    try:
                        return self._update_tokens(request)
                    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidKeyError) as e:
                        return JsonResponse({
                            'status': 'unauthorized',
                            'redirect': '/auth/login',
                            'message': str(e)}, status=status.HTTP_302_FOUND)
                except jwt.InvalidKeyError as e:
                    return JsonResponse({
                        'status': 'unauthorized',
                        'redirect': '/auth/login',
                        'message': str(e)}, status=status.HTTP_302_FOUND)
