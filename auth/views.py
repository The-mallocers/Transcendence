from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

from auth.view.login import login_view
from auth.view.logout import logout_view
from auth.view.register import register_view
from shared.models import User

import pyotp
import json

@csrf_exempt
def register(req):
    return register_view(req)

@csrf_exempt
def login(req):
    return login_view(req)

@csrf_exempt
def logout(req):
    return logout_view(req)

@csrf_exempt
def render_two_fa(req):
    users = User.objects.all()
    context = {"users": users}
    if req.method == 'POST':
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

