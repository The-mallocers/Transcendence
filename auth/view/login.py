from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.conf import settings
from django.core.files.base import ContentFile

from shared.models import Clients
from utils.jwt.TokenGenerator import TokenGenerator, TokenType

import pyotp
import qrcode
import io

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
            if not client.twoFa.scanned:
                get_qrcode(client)
            redirUrl = "/auth/2fa"
        else :
            TokenGenerator(client, TokenType.ACCESS).set_cookie(
                response=response)
            TokenGenerator(client, TokenType.REFRESH).set_cookie(
                response=response)
            redirUrl = "/"
    
        print(redirUrl)
        response = JsonResponse({
            "success": True,
            "message": "You've been corectly login",
            "redirect_url": redirUrl
        }, status=200)
        response.set_cookie(
            key='email',
            value=email,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
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

def get_qrcode(user):
    # create a qrcode and convert it
    print("first_name" + user.profile.username)
    uri = pyotp.totp.TOTP(user.twoFa.key).provisioning_uri(name=user.profile.username, issuer_name="Transcendance_" + str(user.profile.username))
    qr_image = qrcode.make(uri)
    buf = io.BytesIO()
    qr_image.save(buf, "PNG")
    contents = buf.getvalue()
    
    # convert it to adapt to a imagefield type in my db
    image_file = ContentFile(contents, name=f"{user.profile.username}_qrcode.png")
    user.twoFa.update("qrcode", image_file)
    
    return True