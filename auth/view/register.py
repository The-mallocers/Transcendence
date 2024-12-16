import json

import bcrypt
from django.http import JsonResponse
from django.shortcuts import render

from shared.models import User
from utils.jwt.jwt import generate_access_token


def register_view(req):
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
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        nickname = data.get("nickname")
        email = data.get("email")
        password = data.get("password")
        password_verif = data.get("password_verif")

        if (first_name or last_name or nickname or email or password or password_verif) is None:
            return JsonResponse({
                "success": False,
                "message": "Invalid credentials"
            }, status=400)

        if password != password_verif:
            return JsonResponse({
                "success": False,
                "message": "Password miss matching"
            }, status=401)
        try:
            User.objects.get(email=email)
            return JsonResponse({
                "success": False,
                "message": "Account already existe"
            }, status=401)
        except User.DoesNotExist:
            pass

        salt = bcrypt.gensalt(prefix=b'2b')
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode(
            "utf-8")

        user = User(
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            email=email,
            password=password_hash
        )
        user.save()
        response = JsonResponse({
            "success": True,
            "message": "Register successful",
            "redirect_url": "/"
        }, status=200)
        access_token, refresh_token = generate_access_token(user)
        response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='Lax')
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Lax')
        req.session['user_id'] = str(user.id)
        return response

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON format"
        }, status=400)

def get(req):
    users = User.objects.all()
    context = {"users": users}

    return render(req, "auth/register.html", context)
