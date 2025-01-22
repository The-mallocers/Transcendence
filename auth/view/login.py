from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.conf import settings

from shared.models import Clients
from utils.jwt.TokenGenerator import TokenGenerator, TokenType

import pyotp
import qrcode

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
        if client.twoFa.enable:
            two_fa(client)
            print("two fa enable")
            redirUrl = "/auth/2fa"
        else :
            print("two fa disable")
            redirUrl = "/"
        response = JsonResponse({
            "success": True,
            "message": "You've been corectlly login",
            "redirect_url": redirUrl
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

def two_fa(user):
    # check if twofa is activated
    uri = pyotp.totp.TOTP(settings.SECRET_FA_KEY).provisioning_uri(name=user.profile.first_name, issuer_name="Transcendance")
    qrcode.make(uri).save("./static/img/qrcode.png")
    return True