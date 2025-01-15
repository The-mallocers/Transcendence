import json

from django.http import JsonResponse
from django.shortcuts import render

from shared.models import Clients
from utils.jwt.TokenGenerator import TokenGenerator


def post(req):
    try:
        data = json.loads(req.body)
        email = data.get("email")
        password = data.get("password")
        client = Clients.get_client_by_email(email)

        if all(v is None for v in [email, password]):
            return JsonResponse({
                "success": False,
                "message": "Invalid post request"
            }, status=400)

        if client is None:
            return JsonResponse({
                "success": False,
                "message": "Wrong credentials"
            }, status=401)

        if client.password.check_pwd(password):
            token_gen = TokenGenerator()
            response = JsonResponse({
                "success": True,
                "message": "Login successful"
            }, status=200)

            response.set_cookie(
                'access_token',
                token_gen.generate_access_token(client.id),
                httponly=True,
                secure=True,
                samesite='Strict'
            )

            response.set_cookie(
                'refresh_token',
                token_gen.generate_refresh_token(client.id),
                httponly=True,
                secure=True,
                samesite='Strict'
            )
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
    users = Clients.objects.all()

    context = {"users": users}

    return render(req, "auth/login.html", context)