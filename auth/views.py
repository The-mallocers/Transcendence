from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from auth.view.login import login_view
from auth.view.logout import logout_view
from auth.view.register import register_view
from shared.models import User

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
    if req.method == 'POST':
        data = json.loads(req.body)
        print(data)
    users = User.objects.all()
    context = {"users": users}
    return render(req, "auth/2fa.html", context)
