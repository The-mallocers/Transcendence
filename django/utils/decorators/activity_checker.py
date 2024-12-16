import jwt
from django.conf import settings
from django.http import HttpResponse

from shared.models import User
from utils.jwt.jwt import generate_access_token


def activity_checker(view_func):
    def wrapper(request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        user = User.get_user(request)
        try:
            refresh_decoded = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            session_version = refresh_decoded.get('session_version')

            if str(user.session_user) != session_version:
                return HttpResponse('Refresh token revoked')

            _, new_refresh_token = generate_access_token(user)

            response = view_func(request, *args, **kwargs)
            response.set_cookie('refresh_token', new_refresh_token, httponly=True,secure=True, samesite='Lax')
            return response
        except jwt.ExpiredSignatureError:
            return HttpResponse('Refresh token expired')
        except jwt.InvalidTokenError:
            return HttpResponse('Refresh token invalid')
    return wrapper