import bcrypt
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

from shared.models import User
from utils.jwt.jwt import generate_access_token

import pyotp
import qrcode
import json

def login_view(req):
    if req.method == 'GET':
        return get(req)
    if req.method == 'POST':
        return post(req)
    else:
        return JsonResponse({
            "success": False,
            "message": "Method not allowed"
        }, status=405)

def post(req):
    try:
        data = json.loads(req.body)
        email = data.get("email")
        password = data.get("password")
        user = User.objects.filter(email=email).first()

        if (email or password) is None:
            return JsonResponse({
                "success": False,
                "message": "Invalid post request"
            }, status=400)

        if user is None:
            return JsonResponse({
                "success": False,
                "message": "Wrong credentials"
            }, status=401)

        user_password = user.password.encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), user_password):
            access_token, refresh_token = generate_access_token(user)
            response = JsonResponse({
                "success": True,
                "message": "Login successful",
                "redirect_url": "/auth/2fa"
            }, status=200)
            response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='Lax')
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Lax')
            req.session['user_id'] = str(user.id)
            two_fa(req, user)
            return response
        else:
            return JsonResponse({
                "success": False,
                "message": "Wrong credentials"
            }, status=401)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON format"
        }, status=400)

def get(req):
    users = User.objects.all()
    context = {"users": users}

    return render(req, "auth/login.html", context)

def two_fa(req, user):
    if(user.mfa_enable):
        uri = pyotp.totp.TOTP(settings.SECRET_FA_KEY).provisioning_uri(name=user.first_name, issuer_name="Transcendance")
        qrcode.make(uri).save("./static/img/qrcode.png")
        return True
