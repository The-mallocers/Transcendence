from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

from django.http import JsonResponse
from utils.jwt.TokenGenerator import TokenGenerator, TokenType

from auth.view.login import post as post_login, get as get_login
from auth.view.logout import post as post_logout
from auth.view.register import post, get
from shared.models import Clients

import pyotp
import json

@csrf_exempt
@require_http_methods(["POST"])
def register_post(req):
    return post(req)

@require_http_methods(["GET"])
def register_get(req):
    return get(req)

@require_http_methods(["POST"])
def login_post(req):
    return post_login(req)

@require_http_methods(["GET"])
def login_get(req):
    return get_login(req)

@require_http_methods(["POST"])
def logout(req):
    return post_logout(req)

# @csrf_exempt
def view_two_fa(req):
    email = req.COOKIES.get('email')
    print(email)
    if(email):
        client = Clients.get_client_by_email(email)
        print(client)
        context = {"client" : client}
        return render(req,"auth/2fa.html", context)
    return render(req,"auth/2fa.html")
    

def post_twofa_code(req):
    email = req.COOKIES.get('email')
    print("email " + email)
    if email:
        client = Clients.get_client_by_email(email)
        if client is None:
            print("error no client log")
            return render(req, "/auth/login")
        if req.method == 'POST':
            data = json.loads(req.body.decode('utf-8'))
            totp = pyotp.TOTP(client.twoFa.key)
            is_valid = totp.verify(data['code'])
            email = data['code']
            print(email)
            if is_valid:
                if not client.twoFa.scanned:
                    client.twoFa.update("scanned", True)
                TokenGenerator(client, TokenType.ACCESS).set_cookie(
                    response=response)
                TokenGenerator(client, TokenType.REFRESH).set_cookie(
                    response=response)
                response = JsonResponse({
                    "success" : True,
                    "message" : "Login Successful",
                    "redirect_url" : "/"
                }, status=200)
                return response
        print("rendering client")
        response = JsonResponse({
            "success": True,
            "message": "You've been corectlly login",
            "redirect_url": "auth/2fa.html"
        }, status=200)
        return response
    return render(req,"/auth/login.html")

@csrf_exempt
def change_two_fa(req):
    if req.method == "POST":
        data = json.loads(req.body.decode('utf-8'))
        client = Clients.get_client_by_request(req)
        if client is not None :
            client.twoFa.update("enable", data['status'])
            response = JsonResponse({
                "success" : True,
                "message" : "State 2fa change"
            }, status=200)
        else :
            response = JsonResponse({
            "success" : False,
            "message" : "No client available"
        }, status=403)
        return response