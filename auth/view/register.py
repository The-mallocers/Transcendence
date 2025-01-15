import json

from django.http import JsonResponse
from django.shortcuts import render

from account.models import Profile
from shared.models import Clients
from utils.jwt.TokenGenerator import TokenGenerator


def post(req):
    try:
        data = json.loads(req.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        password_check = data.get('password_check')

        if all(v is None for v in
               [first_name, last_name, username, email, password,
                password_check]):
            return JsonResponse({
                "success": False,
                "message": "Incorrect data"
            }, status=400)
        if password != password_check:
            return JsonResponse({
                "success": False,
                "message": "Password missmatch"
            }, status=400)
        if Profile.get_profile(email) is not None:
            return JsonResponse({
                "success": False,
                "message": "Email already existe"
            }, status=400)

        client_id = Clients.create_client(username, first_name, last_name,
                                          email, password)

        token_gen = TokenGenerator()
        response = JsonResponse({
            "success": True,
            "message": "Login successful"
        }, status=200)

        response.set_cookie(
            'access_token',
            token_gen.generate_access_token(client_id),
            httponly=True,
            secure=True,
            samesite='Strict'
        )

        response.set_cookie(
            'refresh_token',
            token_gen.generate_refresh_token(client_id),
            httponly=True,
            secure=True,
            samesite='Strict'
        )

        return response
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON format"
        }, status=400)


def get(req):
    users = Clients.objects.all()

    context = {"users": users}

    return render(req, "auth/register.html", context)
