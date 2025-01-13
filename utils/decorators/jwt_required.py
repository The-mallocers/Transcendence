from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect

from shared.models import Client
from utils.jwt.jwt import generate_access_token

def jwt_required(view_func):
    def wrapper(request, *args, **kwargs):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        if not access_token or not refresh_token:
            return HttpResponseRedirect('/auth/login') # Client unsigned

        try:
            access_decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            session_version =  access_decoded.get("session_version")
            user = User.get_user(request)

            if user is None:
                return HttpResponseRedirect('/auth/login')
            if str(user.session_user) != session_version:
                return HttpResponse("Token revoque", status=401)
        except jwt.ExpiredSignatureError:
            try:
                refresh_decoded = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
                session_version = refresh_decoded.get("session_version")
                user = User.get_user(request)
                if user is None:
                    return HttpResponseRedirect("/auth/login")

                if str(user.session_user) != session_version:
                    return HttpResponse("Token refresh revoked", status=401)

                new_access_token, _ = generate_access_token(user)
                response = view_func(request, *args, **kwargs)
                response.set_cookie('access_token', new_access_token,
                                    httponly=True,
                                    secure=True,
                                    samesite='Lax')
                return response

            except jwt.ExpiredSignatureError:
                return HttpResponse("Reconnection impossible: Token refresh expired", status=401)
            except jwt.InvalidTokenError:
                return HttpResponse("Reconnection impossible: Token refresh invalid",status=401)
        except jwt.InvalidTokenError:
            return HttpResponse("Token invalide", status=401)
        return view_func(request, *args, **kwargs)
    return wrapper