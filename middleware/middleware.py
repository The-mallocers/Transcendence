import re
import secrets
from datetime import datetime, timezone

import jwt
from django.conf import settings
from django.http import JsonResponse, HttpRequest, HttpResponse, \
    HttpResponseRedirect

from shared.models import Clients
from utils.jwt.TokenGenerator import TokenType, Token, TokenGenerator


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.secret_key = getattr(settings, 'JWT_SECRET_KEY')
        self.algorithm = getattr(settings, 'JWT_ALGORITH')
        self.protected_paths = getattr(settings, 'PROTECTED_PATHS')
        self.excluded_paths = getattr(settings, 'EXCLUDED_PATHS')
        self.role_protected_paths = getattr(settings, 'ROLE_PROTECTED_PATHS')
        self.csrf_methods = getattr(settings, 'CSRF_METHODS')

    def _should_check_path(self, path: str) -> bool:
        """Check if the path need to be protected"""
        for excluded in self.excluded_paths:
            if self._path_matches(excluded, path):
                return False

        for protected in self.protected_paths:
            if self._path_matches(protected, path):
                return True
        return False

    def _get_required_roles(self, path: str):
        """Check if the path need to have permission"""
        for pattern, roles in self.role_protected_paths.items():
            if self._path_matches(pattern, path):
                return roles
        return None

    def _path_matches(self, pattern, path: str) -> bool:
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.match(f'^{regex_pattern}$', path))

    def _extract_access_token(self, request: HttpRequest) -> str:
        """Return token key from cookies"""
        token_key: str = request.COOKIES.get('access_token')
        if token_key is None:
            raise jwt.InvalidKeyError(f'Token missing')
        return token_key

    # Return token key
    def _extract_refresh_token(self, request: HttpRequest) -> str:
        """Return token key from cookies"""
        token_key: str = request.COOKIES.get('refresh_token')
        if token_key is None:
            raise jwt.InvalidKeyError(f'Token missing')
        return token_key

    def _generate_csrf_token(self) -> str:
        return secrets.token_urlsafe(32)

    def _validate_csrf(self, request: HttpRequest) -> bool:
        if request.method not in self.csrf_methods:
            return True

        csrf_cookie = request.COOKIES.get('csrf_token')
        csrf_header = request.headers.get('X-CSRF-Token')

        if not csrf_cookie or not csrf_header:
            return False

        return secrets.compare_digest(csrf_cookie, csrf_header)

    def _set_csrf_token(self, response: HttpResponse):
        csrf_token = self._generate_csrf_token()
        response.set_cookie(
            'csrf_token',
            csrf_token,
            httponly=False,
            secure=True,
            samesite='Lax'
        )
        response['X-CSRF-Token'] = csrf_token

    def _validate_token(self, token_key: str, token_type: str) -> Token:
        """Take token key in argument and check the token"""
        try:
            payload = jwt.decode(token_key, self.secret_key,
                                 algorithms=[self.algorithm])
            token = Token.get_token(payload)
            if token.TYPE != token_type:
                raise jwt.InvalidKeyError(
                    f'Invalid token type: {token.TYPE}')
            return token
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError(f'Token {token_type} expired')
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f'Invalid {token_type} token: {str(e)}')

    def _refresh_token(self, request: HttpRequest, response: HttpResponse):
        now = datetime.now(tz=timezone.utc)
        try:
            self._validate_token(self._extract_access_token(request),
                                 TokenType.ACCESS)
        except jwt.ExpiredSignatureError:
            try:
                refresh_token: Token = self._validate_token(
                    self._extract_refresh_token(request), TokenType.REFRESH)
                client: Clients = Clients.get_client_by_id(refresh_token.SUB)
                TokenGenerator(client, TokenType.ACCESS).set_cookie(response)
                TokenGenerator(client, TokenType.REFRESH).set_cookie(response)
            except jwt.ExpiredSignatureError as e:
                raise jwt.ExpiredSignatureError(f'{str(e)}')
            except jwt.InvalidTokenError as e:
                raise jwt.InvalidTokenError(f'{str(e)}')
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f'{str(e)}')

    def __call__(self, request: HttpRequest):
        # Function execute when middleware call
        path = request.path_info
        response = self.get_response(request)

        if not self._should_check_path(path):  # If the not need to be protected
            return self.get_response(request)

        if not self._validate_csrf(request):
            return JsonResponse({
                'error': 'CSRF validation failed'
            }, status=403)

        try:
            token_key: str = self._extract_access_token(request)
            token: Token = self._validate_token(token_key, TokenType.ACCESS)

            request.token_payload = token.get_payload()

            required_roles = self._get_required_roles(path)
            if required_roles:
                user_roles = token.ROLES
                if not any(role in user_roles for role in required_roles):
                    return JsonResponse(
                        {'error': 'Not enough permissions'},
                        status=403
                    )
            self._set_csrf_token(response)
            return response
        except jwt.ExpiredSignatureError as e:
            try:
                self._refresh_token(request, response)
                self._set_csrf_token(response)
                return response
            except Exception as e:
                return HttpResponseRedirect('/auth/login')
        except jwt.InvalidTokenError as e:
            return HttpResponseRedirect('/auth/login')
        except jwt.InvalidKeyError as e:
            return HttpResponseRedirect('/auth/login')
        except Exception as e:
            return JsonResponse(
                {'error': f'Internal server error: {str(e)}'},
                status=500
            )