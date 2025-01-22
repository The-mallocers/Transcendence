from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

from django.conf import settings
from django.http import JsonResponse

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
def render_two_fa(req):
    print("inside rendering two fa")
    users = Clients.objects.all()
    context = {"users": users}
    if req.method == 'POST':
        print("inside post method")
        data = json.loads(req.body.decode('utf-8'))
        print(data['code'])
        totp = pyotp.TOTP(settings.SECRET_FA_KEY)
        is_valid = totp.verify(data['code'])
        if is_valid:
            print("code valid")
            response = JsonResponse({
                "success" : True,
                "message" : "Login Successful",
                "redirect_url" : "/"
            }, status=200)
            return response
    return render(req, "auth/2fa.html", context)

@csrf_exempt
def change_two_fa(req):
    if req.method == "POST":
        data = json.loads(req.body.decode('utf-8'))
        print(data['status'])
        client = Clients.get_client_by_request(req)
        if client is not None :
            print("changing 2fa state")
            client.twoFa.update("enable", data['status'])
            # client.twoFa.enable = data['status']
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