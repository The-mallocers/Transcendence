import fnmatch

import jwt
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from rest_framework import status

from apps.client.models import Clients
from utils.enums import JWTType
from utils.jwt.JWT import JWT


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

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
        
        refresh_token = JWT.extract_token(request, JWTType.REFRESH)
        client = Clients.get_client_by_id(refresh_token.SUB)

        access = JWT(client, JWTType.ACCESS)
        refresh = JWT(client, JWTType.REFRESH)

        request.COOKIES['access_token'] = access.encode_token()
        request.COOKIES['refresh_token'] = refresh.encode_token()

        response = self.get_response(request)

        access.set_cookie(response)
        refresh.set_cookie(response)
        #Claude wants me to invalidate the token at the end
        refresh_token.invalidate_token()

        return response

    def __call__(self, request: HttpRequest):
        if not self.is_path_matching(request.path_info, settings.PROTECTED_PATHS):
            return self.get_response(request)

        elif self.is_path_matching(request.path_info, settings.PROTECTED_PATHS):
            if self._in_excluded_path(request.path_info):
                return self.get_response(request)
            else:
                try:
                    #We dont want to invalidate anything if the access token is good
                    # JWT.extract_token(request, JWTType.REFRESH)
                    JWT.extract_token(request, JWTType.ACCESS) #.invalidate_token()
                    # return self._update_tokens(request)
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
