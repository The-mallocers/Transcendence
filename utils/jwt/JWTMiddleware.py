import fnmatch
import traceback

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
        self.secret_key = getattr(settings, 'JWT_SECRET_KEY')
        self.algorithm = getattr(settings, 'JWT_ALGORITH')

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

    def _update_tokens(self, request: HttpRequest, access_token: JWT = None):
        try:
            refresh_token: JWT = JWT.extract_token(request, JWTType.REFRESH)
            client: Clients = Clients.get_client_by_id(refresh_token.SUB)

            response = self.get_response(request)
            refresh_token.invalidate_token()
            if access_token is not None:
                access_token.invalidate_token()

            access_token = JWT(client, JWTType.ACCESS)
            refresh_token = JWT(client, JWTType.REFRESH)
            request.COOKIES['access_token'] = access_token.encode_token()
            request.COOKIES['refresh_token'] = refresh_token.encode_token()
            request.access_token = access_token

            response = access_token.set_cookie(response)
            response = refresh_token.set_cookie(response)

            return response
        except jwt.ExpiredSignatureError as e:
            raise jwt.ExpiredSignatureError(f'{str(e)}')
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f'{str(e)}')
        except jwt.InvalidKeyError as e:
            raise jwt.InvalidKeyError(f'{str(e)}')

    def __call__(self, request: HttpRequest):
        path = request.path_info

        # on veux checker uniquement les /pages/* car c'est elles qui load le spa.js et on veux checker '/api/*' pour
        # eviter de faire des call a l'api si on est pas connecter
        if self.is_path_matching(path, settings.PROTECTED_PATHS):
            if self._in_excluded_path(path):
                return self.get_response(request)
            else:
                print(f'Path is {path} --------')
                try:
                    print('extract access')
                    request.access_token = JWT.extract_token(request, JWTType.ACCESS)
                    print('after extraxt access')

                    required_roles = self._get_required_roles(path)
                    if required_roles:
                        if not any(role in request.access_token.ROLES for role in required_roles):
                            return JsonResponse({
                                'status': 'unauthorized',
                                'redirect': '/',
                                'message': "You don't have permission"}, status=status.HTTP_401_UNAUTHORIZED)
                    # a ce moment tout les token sont bon, on invalide et recreer les 2 token pour porlonger leur
                    # durer de vie
                    print('before update token in normal')
                    return self._update_tokens(request, request.access_token)
                except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                    try:
                        print('update token in invalid token error')
                        response = self._update_tokens(request)
                        print('return after update')
                        return response
                    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidKeyError) as e:
                        return JsonResponse({
                            'status': 'unauthorized',
                            'redirect': '/auth/login',
                            'message': str(e)}, status=status.HTTP_302_FOUND)
                except jwt.InvalidKeyError:
                    return JsonResponse({
                        'status': 'unauthorized',
                        'redirect': '/auth/login',
                        'message': 'Invalid token'}, status=status.HTTP_302_FOUND)
                except Exception as e:
                    traceback.print_exc()
                    return JsonResponse(
                        {'error': f'Internal server error: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return self.get_response(request)



