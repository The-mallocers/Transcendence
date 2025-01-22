from django.http import JsonResponse, HttpRequest
from django.shortcuts import render

from shared.models import Clients
from utils.jwt.TokenGenerator import TokenGenerator, TokenType


def post(req: HttpRequest):
    email = req.POST.get('email')
    password = req.POST.get("password")
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
        response = JsonResponse({
            "success": True,
            "message": "You've been corectlly login"
        }, status=200)
        TokenGenerator(client, TokenType.ACCESS).set_cookie(
            response=response)
        TokenGenerator(client, TokenType.REFRESH).set_cookie(
            response=response)
        return response
    else:
        return JsonResponse({
            "success": False,
            "message": "Wrong credentials"
        }, status=401)

def get(req):
    users = Clients.objects.all()

    context = {"users": users}

    return render(req, "auth/login.html", context)