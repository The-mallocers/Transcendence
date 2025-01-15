import re

import jwt
from django.conf import settings
from django.http import JsonResponse


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.secret_key = getattr(settings, 'JWT_SECRET_KEY')
        self.algorithm = getattr(settings, 'JWT_ALGORITH')
        self.protected_paths = getattr(settings, 'PROTECTED_PATHS')
        self.excluded_paths = getattr(settings, 'EXCLUDED_PATHS')
        self.role_protected_paths = getattr(settings, 'ROLE_PROTECTED_PATHS')

    def _should_check_path(self, path):
        # Check if the path need to be protected
        for excluded in self.excluded_paths:
            if self._path_matches(excluded, path):
                return False

        for protected in self.protected_paths:
            if self._path_matches(protected, path):
                return True
        return False

    def _get_required_roles(self, path):
        # Check if the path need to have permission
        for pattern, roles in self.role_protected_paths.items():
            if self._path_matches(pattern, path):
                return roles
        return None

    def _path_matches(self, pattern, path):
        # Check if the path is good with a pattern
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.match(f'^{regex_pattern}$', path))

    def _extract_token(self, request):
        # Extract the token from header
        token = request.COOKIES.get('access_token')
        return token

    def _validate_token(self, token):
        # Validate the token
        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            if payload['type'] != 'access':
                raise jwt.InvalidTokenError(
                    f'Invalid token type: {str(payload['type'])}')
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError('Token expired')
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f'Invalid token: {str(e)}')

    def __call__(self, request):
        # Function execute when middleware call
        path = request.path_info

        if not self._should_check_path(path):
            return self.get_response(request)

        try:
            token = self._extract_token(request)
            if not token:
                return JsonResponse(
                    {'error': 'Token missing'},
                    status=401
                )

            payload = self._validate_token(token)
            request.token_payload = payload

            required_roles = self._get_required_roles(path)
            if required_roles:
                user_roles = payload.get('roles', [])
                print(user_roles)
                if not any(role in user_roles for role in required_roles):
                    return JsonResponse(
                        {'error': 'Not enough permissions'},
                        status=403
                    )
            return self.get_response(request)
        except jwt.InvalidTokenError as e:
            return JsonResponse(
                {'error': str(e)},
                status=401
            )
        except Exception as e:
            return JsonResponse(
                {'error': 'Internal server error'},
                status=500
            )
